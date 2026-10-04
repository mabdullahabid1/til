# Test the Merged Result of Concurrent Pull Requests

Two pull requests can pass independently and merge without a textual conflict while still breaking the integration branch. One PR can move or rename an API while another, built against the earlier base, continues importing the old location.

After related pull requests merge, test the actual integration branch rather than relying only on each pull request's checks:

```bash
git fetch origin main
git worktree add ../verify-main --detach origin/main
cd ../verify-main

# Run the smallest import, build, or test that crosses both changes.
python -m compileall .
```

For frequently overlapping work, add a post-merge build on `main` or use a merge queue that tests the combined result before landing it.
