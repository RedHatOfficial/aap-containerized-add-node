# AAP-CONTAINERIZED-INSTALLER

# Table of contents
* [Things to know prior to submitting code](#things-to-know-prior-to-submitting-code)
* [Issue Tracker](#issue-tracker)
* [Prerequisites](#prerequisites)
  * [Fork and clone the aap-containerized-installer repo](#fork-and-clone-the-aap-containerized-installer-repo)
* [Submitting Pull Requests](#submitting-pull-requests)
* [Getting Help](#getting-help)

## Things to know prior to submitting code

- All code submissions are done through pull requests against the `main` branch.
- Take care to make sure no merge commits are in the submission, and use `git rebase` vs `git merge` for this reason.
- If collaborating with someone else on the same branch, consider using `--force-with-lease` instead of `--force`. This will prevent you from accidentally overwriting commits pushed by someone else. For more information, see [git push docs](https://git-scm.com/docs/git-push#git-push---force-with-leaseltrefnamegt).

## Issue Tracker

Issues for the containerized installer are tracked in Jira at [https://issues.redhat.com/browse/AAP](https://issues.redhat.com/browse/AAP) with the component `containerized-installer`.

## Prerequisites
### Fork and clone the aap-containerized-installer repo

If you have not done so already, you'll need to fork the aap-containerized-installer repo on Gitlab. The [GitHub repo](https://github.com/ansible/aap-containerized-installer/) is a mirror from the [Gitlab repo](https://gitlab.cee.redhat.com/ansible/aap-containerized-installer) and all code changes must be submitted there.
For more on how to do this, see [Fork a Repo](https://docs.gitlab.com/user/project/repository/forking_workflow/).

## Submitting Pull Requests

Fixes and Features for aap-containerized-installer will go through the Gitlab pull request process. Submit your pull request (PR) against the `main` branch.

When submitting your PR, ensure to follow the structure from the example below:
- The title must contain the component name and short information about the change
- The description must contain the details about the changes with any relevant data for the review
- The Jira number must be added
```
backup: change x on the backup role

My description about the changes with any details about the implementation
Add here any relevant information about the implementation that facilitates the review.

AAP-12345
```

Here are a few things you can do to help the visibility of your change, and increase the likelihood that it will be accepted:

- No issues when running linters/code checkers
  - `ansible-lint`
- Make the smallest change possible
- Write good commit messages. See [How to write a Git commit message](https://chris.beams.io/posts/git-commit/).

It's generally a good idea to discuss features with us first by engaging on the [#forum-ansible-product-delivery-engineering](https://redhat.enterprise.slack.com/archives/C01ULNLT6AY) slack channel

We like to keep our commit history clean, and will require resubmission of pull requests that contain merge commits. Use `git pull --rebase`, rather than `git pull`, and `git rebase`, rather than `git merge`.

When your PR is initially submitted, wait until the checks are completed and fix any errors that are resulting from your changes.

## Getting Help

If you require additional assistance, please ask on the [#forum-ansible-product-delivery-engineering](https://redhat.enterprise.slack.com/archives/C01ULNLT6AY) slack channel.
