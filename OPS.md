# Pybot Operations Runbook

How pybot is built, deployed, rolled back, and debugged. Each step has a command you can copy. Run all commands from any directory.

Every block below sets its own variables (profile, region, cluster, task ID, saved digest). You can paste any one block alone, in a new shell. A block in `( )` with `set -euo pipefail` stops at the first failed check.

## 1. Overview

```
 PR  ---> CI: build only (no push)
 merge to master ---> CI: build + push ECR pybot:prod AND pybot:latest   (environment ecr-main)
                              |
                              |  nothing deploys by itself
                              v
 you: force new deployment  --> pybot_prod   (the task definition runs pybot:latest)
```

| Item | Value |
|---|---|
| Service | `pybot_prod` (the only one: there is no staging) |
| Image | `pybot:latest` (the task definition does not use `:prod`) |
| Public URL | `pybot.operationcode.org`, paths `/slack/*`, `/pybot/*`, `/airtable/*` only. There is no public health URL. |
| Health signals | target group `ecs-pybot-prod` (path `/health`), ECS task `healthStatus`, the logs |

- Cluster: `operationcode-ecs-us-east-2`. Region: `us-east-2`. The service runs one task.
- The task definition pins a tag, not a digest. ECS resolves the tag to a digest when a task starts.
- The service is defined in [operationcode_infra](https://github.com/OperationCode/operationcode_infra) (`terraform/apps.tf`, `terraform/pybot/`). Change settings there, not by hand.
- Pybot has no database and no migrations. It calls Slack, Airtable, and other APIs.

## 2. How images are built

- A pull request builds the image. It pushes nothing.
- A merge to `master` pushes `pybot:prod` and `pybot:latest`. The job runs in the `ecr-main` environment and does not wait.
- A manual run (Actions > CI > "Run workflow") or a re-run of a push needs `ecr-approval`: a maintainer must approve it. A run on a branch other than `master` pushes only `:staging`, which nothing uses. The approved job runs the `ci.yml` of that branch, and its credentials can also write `:prod` and `:latest`, so read that file before you approve.
- Do not use `docker-build.sh` to deploy. It pushes from a laptop and skips the gates.
- Nothing deploys to ECS automatically. CI never calls ECS. A merge moves `:latest`, but the running task keeps its old image until a new task starts (a deploy, or any restart).
- Security setup (environments, IAM role, trust policy): [`.github/SETUP.md`](.github/SETUP.md).

## 3. Deploy

Deploys cause a short outage: `deployment_minimum_healthy_percent` is 0, `deployment_maximum_percent` is 100, and the deployment circuit breaker is off (all in `terraform/pybot/main.tf`). ECS stops the old task before it starts the new one. If the new task fails, nothing rolls back: you must do section 4.

**Stop rule:** if any step or check below fails, STOP and go to section 4. A `wait services-stable` that times out (about 10 minutes, exit code 255) is a failure.

1. Wait for the CI run on `master` to finish and succeed. This is the run that pushed `:latest`:
   ```bash
   gh run list -R OperationCode/operationcode-pybot --workflow ci.yml --branch master --limit 3
   ```
2. Save the running digest in a file, and print it. You need it for a rollback. A new terminal loses shell variables, the file does not. Run this step one time per deploy, before step 3. It refuses to overwrite a saved digest, so a failed deploy cannot replace the good digest with a bad one. The file `$HOME/pybot-deploy.env` stays until you delete it at the end of step 4 (a good deploy) or at the end of section 4 (a rollback):
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2
     D=$HOME/pybot-deploy.env
     test ! -s $D || { echo "$D exists: a previous deploy or rollback was not finished. If it was finished, run: rm $D. If not, finish it (section 4) first. STOP"; false; }
     T=$(aws ecs list-tasks --cluster $C --service-name pybot_prod --query 'taskArns[0]' --output text)
     G=$(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].containers[0].imageDigest' --output text)
     test -n "$G" -a "$G" != None || { echo "no running digest: STOP"; false; }
     echo "PROD_DIGEST=$G" > $D
     cat $D   # copy this line to your notes
   )
   ```
3. Deploy:
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2
     aws ecs update-service --cluster $C --service pybot_prod --force-new-deployment >/dev/null
     aws ecs wait services-stable --cluster $C --services pybot_prod || { echo "not stable: STOP, roll back (section 4)"; false; }
     echo "deploy stable"
   )
   ```
4. Check. The block prints `CHECKS OK` and exits at the first failed check. On any failure: STOP, and do section 4 (do not run step 5):
   ```bash
   (
     set -euo pipefail
     export AWS_PROFILE=operationcode AWS_REGION=us-east-2
     C=operationcode-ecs-us-east-2
     T=$(aws ecs list-tasks --cluster $C --service-name pybot_prod --query 'taskArns[0]' --output text)
     # a) task HEALTHY, and its digest equals the digest of :latest
     read -r H G < <(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].[healthStatus,containers[0].imageDigest]' --output text)
     L=$(aws ecr describe-images --repository-name pybot --image-ids imageTag=latest --query 'imageDetails[0].imageDigest' --output text)
     test "$H" = HEALTHY || { echo "task health is $H: STOP"; false; }
     test "$G" = "$L" || { echo "task digest $G is not :latest $L: STOP"; false; }
     # b) the target is healthy
     TG=$(aws elbv2 describe-target-groups --names ecs-pybot-prod --query 'TargetGroups[0].TargetGroupArn' --output text)
     TS=$(aws elbv2 describe-target-health --target-group-arn "$TG" --query 'TargetHealthDescriptions[0].TargetHealth.State' --output text)
     test "$TS" = healthy || { echo "target state is $TS: STOP"; false; }
     # c) no errors in the last 15 minutes
     E=$(aws logs filter-log-events --log-group-name ecs-20221213004720404200000001 \
       --log-stream-name-prefix pybot_prod --start-time $(( ($(date +%s) - 900) * 1000 )) \
       --filter-pattern '?Traceback ?ERROR' --query 'events[].message' --output text)
     test -z "$E" || { echo "$E"; echo "errors in the logs: STOP"; false; }
     echo "CHECKS OK"
   )
   ```
5. The deploy is finished and good. Delete the saved digest now, so the next deploy can save a new one:
   ```bash
   rm $HOME/pybot-deploy.env
   ```

## 4. Roll back

Use the digest saved in deploy step 2 (`cat $HOME/pybot-deploy.env`). The task definition runs `:latest`, but `:prod` must match it, so retag both. A tag that already points at the saved digest is skipped. The block stops at the first failed step:

```bash
(
  set -euo pipefail
  export AWS_PROFILE=operationcode AWS_REGION=us-east-2
  C=operationcode-ecs-us-east-2
  . $HOME/pybot-deploy.env
  DIGEST=${PROD_DIGEST:-}
  test -n "$DIGEST" -a "$DIGEST" != None || { echo "no saved digest: STOP"; false; }
  M=$(aws ecr batch-get-image --repository-name pybot --image-ids imageDigest=$DIGEST --query 'images[0].imageManifest' --output text)
  test -n "$M" -a "$M" != None || { echo "no manifest for the digest: STOP"; false; }
  for TAG in latest prod; do
    CUR=$(aws ecr describe-images --repository-name pybot --image-ids imageTag=$TAG --query 'imageDetails[0].imageDigest' --output text 2>/dev/null || true)
    if test "$CUR" = "$DIGEST"; then
      echo ":$TAG already points at $DIGEST: put-image skipped"
    else
      aws ecr put-image --repository-name pybot --image-tag $TAG --image-manifest "$M" >/dev/null
    fi
    N=$(aws ecr describe-images --repository-name pybot --image-ids imageTag=$TAG --query 'imageDetails[0].imageDigest' --output text)
    test "$N" = "$DIGEST" || { echo ":$TAG is $N, not $DIGEST: STOP"; false; }
  done
  aws ecs update-service --cluster $C --service pybot_prod --force-new-deployment >/dev/null
  aws ecs wait services-stable --cluster $C --services pybot_prod || { echo "not stable: STOP"; false; }
  echo "rollback deployed"
)
```

Verify. The block prints `ROLLBACK OK` only if the task digest equals the saved digest, the task is HEALTHY, and the target is healthy:

```bash
(
  set -euo pipefail
  export AWS_PROFILE=operationcode AWS_REGION=us-east-2
  C=operationcode-ecs-us-east-2
  . $HOME/pybot-deploy.env
  T=$(aws ecs list-tasks --cluster $C --service-name pybot_prod --query 'taskArns[0]' --output text)
  read -r H G < <(aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].[healthStatus,containers[0].imageDigest]' --output text)
  test "$H" = HEALTHY || { echo "task health is $H: STOP"; false; }
  test "$G" = "$PROD_DIGEST" || { echo "task digest $G is not $PROD_DIGEST: STOP"; false; }
  TG=$(aws elbv2 describe-target-groups --names ecs-pybot-prod --query 'TargetGroups[0].TargetGroupArn' --output text)
  TS=$(aws elbv2 describe-target-health --target-group-arn "$TG" --query 'TargetHealthDescriptions[0].TargetHealth.State' --output text)
  test "$TS" = healthy || { echo "target state is $TS: STOP"; false; }
  echo "ROLLBACK OK"
)
```

If `ROLLBACK OK` printed, the rollback is finished. Delete the saved digest now, so the next deploy can save a new one:

```bash
rm $HOME/pybot-deploy.env
```

- ECR does not keep tag history. If you did not save the digest, you cannot find the old one by tag.
- The `pybot` ECR repository has no lifecycle policy, so untagged images stay until someone deletes them.
- After a rollback, the next merge to `master` moves `:prod` and `:latest` again. The next restart then runs that new image.

## 5. Run a command in the container (ECS Exec)

ECS Exec is enabled on `pybot_prod` (`enable_execute_command = true`). You need the `session-manager-plugin` (`brew install --cask session-manager-plugin`).

```bash
set -euo pipefail
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
C=operationcode-ecs-us-east-2
T=$(aws ecs list-tasks --cluster $C --service-name pybot_prod --query 'taskArns[0]' --output text)
aws ecs execute-command --cluster $C --task "$T" --container pybot_prod --interactive --command "/bin/sh"
```

Type `exit` to leave. The working directory is `/app`.

**Warning:** this is a shell inside the live production container, and the secrets are in its environment. Do not print them. Prefer read-only commands. The session is recorded only in CloudTrail.

## 6. Secrets

Secrets are in AWS Secrets Manager, in the JSON secret `prod/pybot` (us-east-2). Terraform turns every key of that secret into a task definition secret with the upper-case key as its name. ECS reads the values when a task starts. See `terraform/pybot/main.tf`.

- List the names, never the values:
  ```bash
  export AWS_PROFILE=operationcode AWS_REGION=us-east-2
  aws ecs describe-task-definition --task-definition pybot_prod --query 'taskDefinition.containerDefinitions[0].secrets[].name' --output text
  ```
- To change a value, edit the secret in Secrets Manager, then force a new deployment (deploy step 3). A new key also needs a Terraform apply, because Terraform builds the list of secrets.
- Many values are tokens of other services (Slack, Airtable, and others). Issue the new token at that service first. This runbook has no rotation procedure for them.

## 7. Dependency updates

Policy (see [`.github/dependabot.yml`](.github/dependabot.yml)):

- Dependabot runs each Monday. Python and GitHub Actions: one grouped minor/patch pull request each. Docker: no group and no cooldown, and the `python` base image takes patch updates only.
- Dependabot ignores major versions. A security fix that needs a major shows only as a Dependabot alert. Apply it by hand.
- The cooldown for Python and GitHub Actions is 3 days. It matches the 72-hour supply-chain rule of the org PR reviewer: do not take a release that is less than 72 hours old.
- Never apply a major version, unless a security fix requires it.

To update by hand:

1. Update within the constraints of `pyproject.toml`:
   ```bash
   poetry update
   ```
2. Check the release date of each changed package. Put back any version that is less than 72 hours old (`poetry add "<package>@<previous version>"`, or edit `poetry.lock` back with `git checkout -p poetry.lock`).
3. Run the same checks as CI (the Makefile has them):
   ```bash
   make ci      # ruff check, ruff format --check, pytest with coverage, bandit
   ```
4. Open one pull request with the `pyproject.toml` and `poetry.lock` changes. After the merge, deploy as in section 3.

## 8. Logs and troubleshooting

All containers write to one CloudWatch log group, `ecs-20221213004720404200000001`. The stream prefix is `pybot_prod`.

```bash
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
# Follow the logs
aws logs tail ecs-20221213004720404200000001 --log-stream-name-prefix pybot_prod --follow
# Check that the group name is still correct
aws logs describe-log-groups --log-group-name-prefix ecs-
```

Service state and deployments. `rolloutState` must be `COMPLETED`, and `runningCount` must equal `desiredCount`:

```bash
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
C=operationcode-ecs-us-east-2
aws ecs describe-services --cluster $C --services pybot_prod \
  --query 'services[0].[runningCount,desiredCount,deployments[].[status,rolloutState,taskDefinition],events[:5].message]'
aws ecs list-tasks --cluster $C --service-name pybot_prod --desired-status STOPPED
```

If a new task keeps stopping, read the stop reason. This block reads the newest stopped task:

```bash
set -euo pipefail
export AWS_PROFILE=operationcode AWS_REGION=us-east-2
C=operationcode-ecs-us-east-2
T=$(aws ecs list-tasks --cluster $C --service-name pybot_prod --desired-status STOPPED --query 'taskArns[0]' --output text)
aws ecs describe-tasks --cluster $C --tasks "$T" --query 'tasks[0].[stoppedReason,containers[0].reason]'
```

The container health check (`wget` to `http://localhost:5000/health`) and the target group check (path `/health`) test the same endpoint. Errors are also in Sentry (`SENTRY_DSN` is one of the secrets).
