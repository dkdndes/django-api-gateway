# Git Workflow

This document outlines the Git workflow for the Django API Gateway project.

## Branch Structure

- `main`: The production-ready branch. All releases are tagged from this branch.
- `develop`: The integration branch. All feature branches are merged into this branch before being merged into `main`.
- Feature branches: Created from `develop` and merged back into `develop` when complete.

## Branch Naming Conventions

- `feature/`: For new features (e.g., `feature/add-jwt-authentication`)
- `bugfix/`: For bug fixes (e.g., `bugfix/fix-header-handling`)
- `hotfix/`: For critical fixes that need to be applied directly to `main` (e.g., `hotfix/security-vulnerability`)
- `chore/`: For maintenance tasks (e.g., `chore/update-dependencies`)
- `docs/`: For documentation updates (e.g., `docs/update-api-docs`)

## Workflow Steps

1. **Create a Feature Branch**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Develop and Commit Changes**:
   ```bash
   # Make changes
   git add .
   git commit -m "feat: add your feature"
   ```

3. **Push Feature Branch to Remote**:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. **Create Pull Request**:
   Create a pull request from your feature branch to `develop`.

5. **Review and Merge**:
   After code review, merge the feature branch into `develop`.

6. **Release Process**:
   When ready for a release:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout main
   git pull origin main
   git merge develop
   git push origin main
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

## Default Branch

The default branch for this repository is `main`. All production code should be merged into this branch.

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- MAJOR version when you make incompatible API changes
- MINOR version when you add functionality in a backwards compatible manner
- PATCH version when you make backwards compatible bug fixes