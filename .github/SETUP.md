# GitHub Actions Docker Push Setup

This guide gives the setup that CI must have to push Docker images to ECR. It also gives the security rules for that setup.

## How pushes are gated

Only maintainers can cause CI to push an image through the pybot role. The workflow file does not enforce this, because a writer can change the file on a branch. GitHub Environments and the AWS trust policy enforce it.

```
pull_request (any author)     --> docker-build        build only, no AWS credentials
push to master, first attempt --> docker-build-push   environment ecr-main      no wait
workflow_dispatch (any ref)   --> docker-build-push   environment ecr-approval  maintainer approves
re-run of any push run        --> docker-build-push   environment ecr-approval  maintainer approves
                                         |
                                         v
     role GitHubActions-ECR-Push-pybot trusts ONLY the ecr-main and ecr-approval subjects
```

- `ecr-main` can skip the wait because the org ruleset on `master` requires a pull request with code-owner review.
- Image tags: `:prod` and `:latest` when the ref is `master`, and `:staging` for all other refs. All tags are in the same ECR repository, `pybot`.
- Pull requests, Dependabot and forks included, never get AWS credentials. Branch and PR pushes do not publish `:staging`. A maintainer pushes `:staging` with a dispatch (see [Push a Staging Image](#push-a-staging-image-maintainers)).

## Required Secret

- **`AWS_ROLE_ARN`** (repository secret): the ARN of the IAM role that the push job assumes.

```bash
gh secret set AWS_ROLE_ARN --repo OperationCode/operationcode-pybot --body "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push-pybot"
```

## Required Environments

Create the two environments in Settings > Environments. Create them **before** a workflow uses them. If a workflow uses an environment that does not exist, GitHub creates it with no protection rules.

| Environment | Required reviewers | Deployment branches and tags |
|---|---|---|
| `ecr-main` | None | "Selected branches and tags", with one **branch** rule: `master`. Do not add a tag rule. Do not use "Protected branches only". |
| `ecr-approval` | `irvingpop` and `kylemh` | No restriction |

- The owner chose the `ecr-approval` reviewers. The owner can change them later in Settings > Environments > `ecr-approval`. GitHub allows at most 6 users or teams. Add only maintainers. Do not add a team that has only write access (for example `contributors` or `core-contributors`).
- One approval from a reviewer is sufficient.

Check the environments after you create them:

```bash
gh api repos/OperationCode/operationcode-pybot/environments \
  --jq '.environments[] | {name, protection_rules, deployment_branch_policy}'
gh api repos/OperationCode/operationcode-pybot/environments/ecr-main/deployment-branch-policies \
  --jq '.branch_policies[] | {name, type}'
# Expect exactly one policy: {"name":"master","type":"branch"}
```

The old environments `oc-pybot-production` and `oc-pybot-staging` are not used by any workflow, and no role trusts them.

## AWS Role

The pybot repository has its own role, `GitHubActions-ECR-Push-pybot`. No other repository uses it.

### Trust policy

The repository uses immutable OIDC subjects. To get the prefix, run this command:

```bash
gh api repos/OperationCode/operationcode-pybot/actions/oidc/customization/sub --jq .sub_claim_prefix
# repo:OperationCode@10479364/operationcode-pybot@146210805
```

Save this as `pybot-trust.json`:

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
- Use `StringEquals` and these two subjects only. Do not use `StringLike` or `*`.
- Do not add `:pull_request` or `:ref:refs/heads/...` subjects. A writer can get those subjects without approval.
- Do not add subjects of another repository. Each repository gets its own role.
- The role must have only this one `Allow` statement. Examine all statements with this command:
  `aws iam get-role --role-name GitHubActions-ECR-Push-pybot --query Role.AssumeRolePolicyDocument`

### Permissions policy (inline)

Save this as `pybot-ecr-push.json`. The first statement has the ECR actions of the push job, on the `pybot` repository only. `ecr:GetAuthorizationToken` (used by `amazon-ecr-login`) cannot be limited to a repository, so it has its own statement on `*`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:us-east-2:633607774026:repository/pybot"
    },
    {
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    }
  ]
}
```

### Create the role

The role is defined in [operationcode_infra](https://github.com/OperationCode/operationcode_infra), file `terraform/github_actions_ecr.tf`. Apply it with Terraform. Do not create the role by hand, and do not edit it by hand.

The trust policy and permissions policy above are a reference only. The Terraform file is the source of truth.

To examine the result after the apply:

```bash
aws iam get-role --role-name GitHubActions-ECR-Push-pybot \
  --query 'Role.[Arn,MaxSessionDuration,AssumeRolePolicyDocument]'
aws iam list-role-policies --role-name GitHubActions-ECR-Push-pybot           # only ecr-push-pybot
aws iam list-attached-role-policies --role-name GitHubActions-ECR-Push-pybot  # empty
```

## The Old Shared Role

The old shared role `GitHubActions-ECR-Push` was deleted on 2026-11-23, after both repositories moved to their own roles. The CloudTrail check of its window was clean.

## Safe Change to the New Role

Done on 2026-11-23. Kept as a record: do not run it again. It moved pybot from the old shared role to its own role.

1. Create the two environments, as given in [Required Environments](#required-environments). Write down the time when you start this step (S).
2. Create the new role, as given in [Create the role](#create-the-role). Get the pull request that adds the environments to `ci.yml` approved and green. Do not merge it yet.
3. Set the secret to the new role ARN, as given in [Required Secret](#required-secret).
   - Between step 3 and step 5, every push run of the old workflow fails at "Configure AWS credentials", because the new role does not trust its subject. Nobody must push to `master` during this time.
4. Cancel every pybot CI run that is in progress or queued. These runs can hold the old ARN or credentials of the old role.
   ```bash
   # List the runs, then cancel each one.
   for s in in_progress queued; do
     gh run list --repo OperationCode/operationcode-pybot --status $s --limit 100 --json databaseId --jq '.[].databaseId'
   done | xargs -n 1 gh run cancel --repo OperationCode/operationcode-pybot
   ```
   To cancel one run: `gh run cancel <id> --repo OperationCode/operationcode-pybot`. Run the list again until it is empty.
5. Immediately merge the pull request. The push to `master` that the merge causes uses `ecr-main` and the new role, and pushes `:prod` and `:latest`.
   - If the first push fails, correct the new role (see the rules above). Then re-run the job. The re-run uses `ecr-approval`, so a maintainer must approve it.
   - When the push run is complete, write down the image digest of `:prod`.:
     `aws ecr describe-images --region us-east-2 --repository-name pybot --image-ids imageTag=prod --query 'imageDetails[0].imageDigest' --output text`
6. Confirm one successful push to `master` through the new role. Use one of these:
   - CloudTrail: find the `AssumeRoleWithWebIdentity` event for the new role ARN, at the time of the push run from step 5.
     ```bash
     aws cloudtrail lookup-events --region us-east-2 \
       --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRoleWithWebIdentity \
       --start-time <merge time> --output json |
       jq -r '.Events[] | (.CloudTrailEvent | fromjson) as $c
         | select($c.requestParameters.roleArn == "arn:aws:iam::633607774026:role/GitHubActions-ECR-Push-pybot")
         | [.EventTime, $c.requestParameters.roleArn, ($c.userIdentity.userName // "-"), ($c.errorCode // "ok")] | @tsv'
     ```
     Expect a line with `ok` and the subject `...:environment:ecr-main`.
   - Run log: the push run from step 5 shows environment `ecr-main`, and the "Output image URI" step prints `Successfully pushed Production images`.

   The pybot move is done after this step.

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
- Compare the trust subjects with the prefix from `gh api .../actions/oidc/customization/sub`. The subject is `<prefix>:environment:<environment name>`. Never add an old subject back.

### Build fails with "AccessDenied" to ECR
- Make sure that the role has the inline policy `ecr-push-pybot`.
- Make sure that the repository is `633607774026.dkr.ecr.us-east-2.amazonaws.com/pybot`.

### Production build runs even when tests fail
- This must not occur. The push job depends on the `ci-success` job.
- Make sure that `ci-success` fails when lint or tests fail.

## Additional Resources

- [GitHub Actions secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc)
- [AWS OIDC with GitHub](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
