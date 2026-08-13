# AAP-CONTAINERIZED-INSTALLER

# Table of contents
* [Things to know before submitting code](#things-to-know-before-submitting-code)
* [Issue Tracker](#issue-tracker)
* [Prerequisites](#prerequisites)
  * [Fork and clone the aap-containerized-installer repo](#fork-and-clone-the-aap-containerized-installer-repo)
  * [Review the development templates](#review-the-development-templates)
  * [Testing your changes](#testing-your-changes)
  * [Validating your changes using an approved AI Assistant](#validating-your-changes-using-an-approved-ai-assistant)
* [Submitting Pull Requests](#submitting-pull-requests)
* [Creating the backport for a merged Pull Request](#creating-the-backport-for-a-merged-pull-request)
  * [Troubleshooting Backports](#troubleshooting-backports)
* [Getting Help](#getting-help)

## Things to know before submitting code

- All code submissions are done through pull requests against the `main` branch.
- Take care to make sure no merge commits are in the submission, and use `git rebase` vs `git merge` for this reason.
- If collaborating with someone else on the same branch, consider using `--force-with-lease` instead of `--force`. This will prevent you from accidentally overwriting commits pushed by someone else. For more information, see [git push docs](https://git-scm.com/docs/git-push#git-push---force-with-leaseltrefnamegt).

## Issue Tracker

Issues for the containerized installer are tracked in Jira at [https://issues.redhat.com/browse/AAP](https://issues.redhat.com/browse/AAP) with the component `containerized-installer`.

## Prerequisites
### Fork and clone the aap-containerized-installer repo

If you have not done so already, you'll need to fork the aap-containerized-installer repo on GitLab. The [GitHub repo](https://github.com/ansible/aap-containerized-installer/) is a mirror of the [Gitlab repo](https://gitlab.cee.redhat.com/ansible/aap-containerized-installer), and all code changes must be submitted there.
For more on how to do this, see [Fork a Repo](https://docs.gitlab.com/user/project/repository/forking_workflow/).

### Review the development templates

Review the `dev/` folder for development tools and guidance on modifying existing components or adding new ones to the installer.

### Testing your changes

Use the [testing guide](dev/TESTING.md) for the necessary steps to test your changes in a VM.

### Validating your changes using an approved AI Assistant

Using your preferred AI assistant, follow the [instructions](./.claude/README.md) for reviewing a component or PR. Coding standards are available as [Agent Skills](./.agents/skills/) compatible with Claude Code, Cursor, Windsurf, and other AI tools.

**NOTE:** We strongly recommend reviewing your changes before opening a Pull Request as this will assist with spotting inconsistencies and simple errors.
Note that not all the AI suggestions are applicable to your code but are a good start for reviewing the changes.

## Submitting Pull Requests

Fixes and Features for aap-containerized-installer will go through the GitLab pull request process. Submit your pull request (PR) against the `main` branch.

When submitting your PR, ensure to follow the structure from the example below:
- The title must contain the component name and short information about the change
- The description must contain the details about the changes, with any relevant data for the review
- The Jira number must be added
```
backup: change x on the backup role

My description of the changes, with any details about the implementation
Add here any relevant information about the implementation that facilitates the review.

AAP-12345
```
- Squash your changes into a single commit before submitting to maintain clean history and simplify backporting

Here are a few things you can do to help the visibility of your change and increase the likelihood that it will be accepted:

- No issues when running linters/code checkers
  - `ansible-lint`
- Make the smallest change possible
- Write good commit messages. See [How to write a Git commit message](https://chris.beams.io/posts/git-commit/).

It's generally a good idea to discuss features with us first by engaging on the [#forum-ansible-product-delivery-engineering](https://redhat.enterprise.slack.com/archives/C01ULNLT6AY) Slack channel

We like to keep our commit history clean, and will require resubmission of pull requests that contain merge commits. Use `git pull --rebase`, rather than `git pull`, and `git rebase`, rather than `git merge`.

After submitting your PR, monitor the automated checks and address any failures or errors that arise from your changes.
If `functional_tests` don't start automatically, request a manual trigger in the [#forum-ansible-product-delivery-engineering](https://redhat.enterprise.slack.com/archives/C01ULNLT6AY) Slack channel.

## Creating the backport for a merged Pull Request

After a change has been merged in the main branch, the backport can be created for the desired/necessary releases.

- Ensure the backport Jira is properly labeled, the `Target Version`, `Release Notes Type`, `Release Note Text` and `Test Link` are properly filled
- Create a PR branch name prefixed with the release version
  - **Note:** `upstream` refers to the main repository, `origin` refers to your fork
```
$ git checkout -b 2.6/my-change-pr upstream/stable-2.6
$ git cherry-pick -x xxxxxxxxxxxxxxxxxxxxx
$ git push origin 2.6/my-change-pr
```
- Create the Backport adding the merged PR ID and Jira Number into the description
- Make sure to select the correct target branch for your backport
- Title the backport with the release name
```
Title: [stable-2.6] backup: change x on the backup role
```
- The description will look like this example
```
backup: change x on the backup role

My description of the changes, with any details about the implementation
Add here any relevant information about the implementation that facilitates the review.

AAP-23456

Backports: !99

Signed-off-by: Lucas Benedito <lbenedit@redhat.com>
(cherry picked from commit xxxxxxx)
```
- Notify in the Slack channel [#forum-ansible-product-delivery-engineering](https://redhat.enterprise.slack.com/archives/C01ULNLT6AY) with the backport link. If you need to add comments, please create a thread to contain all the information in one place.

### Troubleshooting Backports

**Cherry-pick conflicts:**
If you encounter merge conflicts during cherry-pick:
```
$ git cherry-pick -x xxxxxxxxxxxxxxxxxxxxx
# Resolve conflicts in the affected files
$ git add <resolved-files>
$ git cherry-pick --continue
```

**Multiple commits to backport:**
If your change spans multiple commits, cherry-pick them in order:
```
$ git cherry-pick -x commit1 commit2 commit3
```

**Dependencies between changes:**
If your backport depends on another change that isn't in the target branch yet, ensure the dependency is backported first or mention it in the PR description.

## Getting Help

If you require additional assistance, please ask on the [#forum-ansible-product-delivery-engineering](https://redhat.enterprise.slack.com/archives/C01ULNLT6AY) Slack channel.