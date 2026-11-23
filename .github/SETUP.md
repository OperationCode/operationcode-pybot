# GitHub Actions Docker Push Setup

This guide gives the setup that CI must have to push Docker images to ECR. It also gives the security rules for that setup.

## How pushes are gated

Only maintainers can cause CI to push an image. The workflow file does not enforce this, because a writer can change the file on a branch. GitHub Environments and the AWS trust policy enforce it.

```
pull_request (any author)     --> docker-build        build only, no AWS credentials
push to master, first attempt --> docker-build-push   environment ecr-main      no wait
workflow_dispatch (any ref)   --> docker-build-push   environment ecr-approval  maintainer approves
re-run of any push run        --> docker-build-push   environment ecr-approval  maintainer approves
                                         |
                                         v
     AWS role GitHubActions-ECR-Push-pybot trusts ONLY the ecr-main and ecr-approval subjects
```

- `ecr-main` can skip the wait because the org ruleset on `master` requires a pull request with code-owner review.
- Image tags: `:prod` and `:latest` when the ref is `master`, and `:staging` for all other refs. All tags are in the same ECR repository, `pybot`.
- Pull requests, Dependabot and forks included, never get AWS credentials. Branch and PR pushes do not publish `:staging`. A maintainer pushes `:staging` with a dispatch (see [Push a Staging Image](#push-a-staging-image-maintainers)).

## Required Secret

- **`AWS_ROLE_ARN`**: the ARN of the IAM role that the push job assumes: `arn:aws:iam::633607774026:role/GitHubActions-ECR-Push-pybot`.

```bash
gh secret set AWS_ROLE_ARN --repo OperationCode/operationcode-pybot --body "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push-pybot"
```

## Required Environments

Create the two environments in Settings > Environments. Create them **before** a workflow uses them. If a workflow uses an environment that does not exist, GitHub creates it with no protection rules.

| Environment | Required reviewers | Deployment branches and tags |
|---|---|---|
| `ecr-main` | None | "Selected branches and tags", with one **branch** rule: `master`. Do not add a tag rule. Do not use "Protected branches only". |
| `ecr-approval` | The code owner `irvingpop` and the maintainers | No restriction |

Get the reviewers from GitHub. Do not copy them from an old list:

```bash
# Code owners
gh api repos/OperationCode/operationcode-pybot/contents/.github/CODEOWNERS --jq .content | base64 -d
# Maintainers: users with the admin or maintain role on the repository
gh api repos/OperationCode/operationcode-pybot/collaborators --paginate \
  --jq '.[] | select(.role_name == "admin" or .role_name == "maintain") | .login'
```

Do not add a team that has only write access (for example `contributors` or `core-contributors`) as a reviewer.

Check the environments after you create them:

```bash
gh api repos/OperationCode/operationcode-pybot/environments \
  --jq '.environments[] | {name, protection_rules, deployment_branch_policy}'
gh api repos/OperationCode/operationcode-pybot/environments/ecr-main/deployment-branch-policies \
  --jq '.branch_policies[] | {name, type}'
# Expect exactly one policy: {"name":"master","type":"branch"}
```

The old environments `oc-pybot-production` and `oc-pybot-staging` are not used by any workflow. The AWS role does not trust them.

## AWS Role `GitHubActions-ECR-Push-pybot`

Pybot has its own role. The shared role `GitHubActions-ECR-Push` is for `back-end` only, and must not trust pybot or allow `repository/pybot`.

### Trust policy

The repository uses immutable OIDC subjects. To get the prefix, run this command:

```bash
gh api repos/OperationCode/operationcode-pybot/actions/oidc/customization/sub --jq .sub_claim_prefix
# repo:OperationCode@10479364/operationcode-pybot@146210805
```

The trust must use `StringEquals` and these two subjects only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::633607774026:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": [
            "repo:OperationCode@10479364/operationcode-pybot@146210805:environment:ecr-main",
            "repo:OperationCode@10479364/operationcode-pybot@146210805:environment:ecr-approval"
          ]
        }
      }
    }
  ]
}
```

Rules:
- Do not use `StringLike` or `*`.
- Do not add `:pull_request` or `:ref:refs/heads/...` subjects. A writer can get those subjects without approval.
- The role must have only this one statement. Examine it with this command:
  `aws iam get-role --role-name GitHubActions-ECR-Push-pybot --query Role.AssumeRolePolicyDocument`

### Permission policy

ECR push to `repository/pybot` only. `GetAuthorizationToken` does not support a resource, so it has its own statement.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PushPybot",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:us-east-2:633607774026:repository/pybot"
    },
    {
      "Sid": "EcrLogin",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    }
  ]
}
```

## Safe Switch-over

Use this procedure to move from the shared role to `GitHubActions-ECR-Push-pybot`. It makes sure that no unapproved credential path stays open during the change.

1. Create the two environments, as given in [Required Environments](#required-environments).
2. Create the role `GitHubActions-ECR-Push-pybot` with the trust and permission policies above.
3. Get the pull request that adds the environments to `ci.yml` approved and green. Do not merge it yet.
4. Set the secret `AWS_ROLE_ARN` to the new role, as given in [Required Secret](#required-secret).
5. Remove pybot from the shared role `GitHubActions-ECR-Push`, in one change for each policy:
   - Trust: remove every `operationcode-pybot` subject (all spellings, the name form and the ID form). If the back-end switch-over is already done, the trust has only the back-end environment subjects. Examine it:
     `aws iam get-role --role-name GitHubActions-ECR-Push --query Role.AssumeRolePolicyDocument`
   - Permission: remove `repository/pybot` from `GitHubActions-ECR-Push-Policy`.

   Write down the time of this change (T). After T, the shared role cannot issue a new session to pybot CI.
6. Cancel every pybot CI run that is in progress or queued. These runs can hold credentials from before T.
   ```bash
   # List the runs, then cancel each one.
   for s in in_progress queued; do
     gh run list --repo OperationCode/operationcode-pybot --status $s --limit 100 --json databaseId --jq '.[].databaseId'
   done | xargs -n 1 gh run cancel --repo OperationCode/operationcode-pybot
   ```
   Run the list again until it is empty.
7. Revoke the sessions of the shared role: IAM > Roles > `GitHubActions-ECR-Push` > "Revoke active sessions". Write down the time of this revoke (R). This also stops running back-end push jobs. Do it when no back-end push is running.
8. Immediately merge the pull request. The push to `master` that the merge causes uses `ecr-main` and pushes `:prod` and `:latest`.
   - Between step 4 and step 8, every push run of the old workflow fails at "Configure AWS credentials". Nobody must push to `master` during this time.
   - If the first push fails, correct the trust subject (see the rules above). Then re-run the job. The re-run uses `ecr-approval`, so a maintainer must approve it.
   - When the push run is complete, write down the image digest of `:prod`. You compare with it in step 9:
     `aws ecr describe-images --region us-east-2 --repository-name pybot --image-ids imageTag=prod --query 'imageDetails[0].imageDigest' --output text`
9. Check for ECR login tokens from before R. A session issued before T can call ECR `GetAuthorizationToken` until the revoke at R. An ECR login token stays valid for 12 hours, and AWS does not document that "Revoke active sessions" stops it. Thus such a token can push until R + 12 h. An unapproved push during this window is detected, not prevented. When you follow these steps, you accept this risk.
   - At R + 12 h plus approximately 30 minutes (CloudTrail can deliver events late), list the ECR write events from T - 12 h to R + 12 h:
     ```bash
     for e in InitiateLayerUpload PutImage BatchDeleteImage; do
       aws cloudtrail lookup-events --region us-east-2 \
         --lookup-attributes AttributeKey=EventName,AttributeValue=$e \
         --start-time <T-12h> --end-time <R+12h> --output json |
         jq -r '.Events[] | (.CloudTrailEvent | fromjson) as $c
           | [.EventTime, .EventName, .Username,
              ($c.userIdentity.sessionContext.sessionIssuer.arn // "-"),
              ($c.requestParameters.repositoryName // "-"),
              ($c.sourceIPAddress // "-")] | @tsv'
     done
     ```
     The columns are: time, event, `Username`, session issuer ARN, ECR repository, source IP address. Use the session issuer ARN to find the events of the CI roles (`role/GitHubActions-ECR-Push` and `role/GitHubActions-ECR-Push-pybot`). Do not use `Username` for this: for a role session it is the session name, and the caller chooses it. Each event of a CI role on the `pybot` repository must match a pybot CI run that you know about (time and run).
   - The `PutImage` events are the real control. The tag check below shows only the current state of each tag.
   - At the same time, make sure that the `:prod`, `:latest` and `:staging` digests are the digests that known CI runs pushed. For `:prod` and `:latest`, this is the digest from step 8, unless a later known run pushed them:
     ```bash
     for t in prod latest staging; do
       aws ecr describe-images --region us-east-2 --repository-name pybot \
         --image-ids imageTag=$t --query 'imageDetails[].[imageTags,imageDigest,imagePushedAt]'
     done
     ```
     An `ImageNotFoundException` for a tag means that the tag does not exist. This is not a failure of the check.
   - If an event or a digest does not match, push a known-good image again (re-run the master build with an `ecr-approval` approval) and investigate.

## Push a Staging Image (maintainers)

Pull requests do not push images. To push `:staging` from a branch:

1. Go to Actions > CI > "Run workflow". Select the branch. You can also run `gh workflow run ci.yml --repo OperationCode/operationcode-pybot --ref <branch>`.
2. The `Build and Push Docker Image` job waits for the `ecr-approval` review.
3. Before you approve, read the commit **and** `.github/workflows/ci.yml` on that branch. The approved job runs with the branch's workflow file. Its credentials can also write `:prod` and `:latest`.
4. Approve the deployment. The job pushes `pybot:staging`.

A dispatch on `master` pushes `:prod` and `:latest`, and it also needs approval.

## Troubleshooting

### Build fails with "Error assuming role"
- Make sure that the `AWS_ROLE_ARN` secret is the ARN of `GitHubActions-ECR-Push-pybot`.
- Make sure that the job ran in `ecr-main` or `ecr-approval` (the job page shows the environment).
- Compare the trust subjects with the prefix from `gh api .../actions/oidc/customization/sub`. The subject is `<prefix>:environment:<environment name>`.

### Build fails with "AccessDenied" to ECR
- Make sure that the role has the permission policy above.
- Make sure that the repository is `633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot`.

### Production build runs even when tests fail
- This must not occur. The push job depends on the `ci-success` job.
- Make sure that `ci-success` fails when lint or tests fail.

## Additional Resources

- [GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc)
- [AWS OIDC with GitHub](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
