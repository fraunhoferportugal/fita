# Contributing to FITA

Thanks for wanting to contribute! This file explains the minimal rules we follow so PRs can be reviewed and merged quickly.

## Table of Contents
- [Quick Start](#quick-start)
- [Local Development & Tests](#local-development--tests)
- [Pull Request Workflow](#pr-workflow)
  - [CI Checks (Required)](#ci-checks-required)
  - [Labels](#labels)
- [Version Management](#version-management)
- [Releases](#releases)
- [Issue Reports and Feature Requests](#issue-reports-and-feature-requests)
- [Code of Conduct](#code-of-conduct)

## Quick start
1. Fork the repo and create a branch for your contribution: `git checkout -b [feature|fix|ci]/my-change`
2. Write code against `development`. Prefer small, focused PRs.

## Local Development & Tests
FITA is composed of multiple components with different responsibilities.
This is the main project repo, which acts as an aggregator of related components,
linked as `git` submodules. 

You can clone this repo and its submodules to as a way to have a complete development environment
with global component visibility and testing.

> [!IMPORTANT]
> Changes to component source code must be made in the corresponding submodule repository.
> This repository should only contain:
> - Submodule references
> - Distribution configuration
> - Helm chart aggregation
> - Documentation

Check the `CONTRIBUTING.md` of each of the component submodules to ensure environment requirements
and the available tests.

## PR Workflow
- Open a PR against `development`.
- Use a descriptive title and reference the issue: `Fix: <short desc> (#123)`
- PR body checklist:
    - Documentation compiles locally
- At least two approving reviews from a maintainer required. Maintainers may request changes — please address them with new commits on the same branch.

### CI checks (required)
- `Update and Test Documentation on PR` workflow - (`main` and `development` branches)  
    This workflow ensures the documentation website still builds directory
    despite changes to the `website/` directory

If a CI job fails, fix the issue or add a clear PR comment explaining why a job can be skipped.

### Labels

This repository uses labels to help with some management tasks.
| Label | Description |
| --- | --- |
| `no-tag` | Keeps workflows from tagging the merge commit in the `main` branch and creating a release draft on pull requests merges targeting main. |
| `needs-triage` | Default label, indicating a maintainer is to correctly tag the issue |

## Version Management
FITA component versioning follows a [semantic versioning (semver)](https://semver.org/) inspired scheme.

### Synchronizing component updates
The `Update component releases` workflow runs periodically (Mondays at 3 am) to check if submodule repositories have pushed new tags, announcing new versions of FITA components. This workflow can also be triggered manually.

If new versions are available, the workflow opens or updates a PR using the `development` branch as base and with the title: `[relsync] Update submodule releases`. In this PR, the workflow uses [RelSync](https://github.com/fraunhoferportugal/RelSync) to track submodule commits pointed by the new tags and to update the component Helm chart versions used as FITA Helm chart dependencies, bumping the FITA chart version using the following heuristic:
| Submodule Chart Bump | FITA Chart Bump | Description |
| --- | --- | --- |
| `patch` | `patch` | A patch causes the version to be incremented by a patch |
| `minor` | `patch` | The API and components remain the same. Only new backwards compatible features and improvements are introduced. |
| `major` | `minor` | Indicates potentially breaking API changes in one or more FITA components. |
| NA | `major` | New architectural components in the FITA framework maintainer decision. |

To automate version bumps, to be used with the `release` bump type in the `Bump, tag and release main` workflow, `relsync` adds the `relsync/base-version` and `relsync/bump` annotations to the FITA Helm chart, in `deploy/chart/Chart.yaml`, which it keeps updated according to the heuristic.

Additionally, a development identifier is added to the Helm chart version, `<version>-development`.
If `relsync` has run updated the `development` branch multiple times without a release, the identifier is suffixed with a counter for the number of updates, `<new-version>-development.<n>`.

### FITA Versioning

Version bumps are automated through Pull Request discussions using the `Bump, tag and release main` workflow and RelSync.
When a PR targeting main is merged without the no-tag label`, the workflow:
1. Determines the version bump type from the latest PR discussion comment:
    ```
    !relsync bump (major|minor|patch|release)
    ```
    The `major`, `minor` and `patch` bump types increment the chart version accordingly. The `release` bump type  removes the development suffix after submodule synchronization. (e.g., 0.0.3-development.1 → 0.0.3)

    If no bump type is provided (either via PR comment or relsync annotations in deploy/chart/Chart.yaml), the workflow fails.
2. Updates the Helm chart in /deploy/chart, including dependencies and version.
3. Creates a new documentation version using Docusaurus versioned docs.
4. Commits these changes, creates a Git tag pointing to that commit, and pushes it.

After the tag is pushed, the documentation deployment workflow runs automatically.

## Releases
FITA releases are handled by the `Release` workflow. 
This workflow is triggered either by a tag being pushed to the repository or
by the `Bump, tag and release main` workflow.

The workflow will first validate the provided tag is a valid SemVer string.
Then, it publishes the corresponding Helm chart to the GitHub Container Registry as an OCI artifact.
Finally, creates or updates a draft GitHub release and also uploads the chart as its artifact.

Additionally, if the workflow was triggered by the `Bump, tag and release main`,
after the `Release` workflow completes, the `Bump, tag and release main` workflow merges back Helm chart and website updates to the `development` branch.

## Documentation Website

The `Deploy Documentation to GitHub Pages` workflow is triggered by pushes changing the `website/` directory in either the `development` or `main` branches, excluding commits containing the string `[skip ci]` in their message.

The workflow builds and deploys the documentation website to GitHub Pages.

## Issue reports and Feature Requests
When opening an issue make sure you are targeting the correct FITA sub-repo. You can check them anytime in the [architecture docs](https://fraunhoferportugal.github.io/fita/docs/) and in the main repo in the [`components/` directory](https://github.com/fraunhoferportugal/fita/tree/development/components).

In your issue report, please include the following:
- Reproduction steps
- Version/commit hash
- Relevant logs and config snippets

If you're submitting a feature request, please include a motivation or use case for your request and, optionally, a solution proposal.
