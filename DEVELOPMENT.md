#  Notebook Development Workflow

This guide explains how to update and publish notebooks consistently.

---

## 1. Run your notebooks
Open the `.ipynb` file you changed and **run all cells** so that the outputs are visible.

---

## 2. Create HTML snapshots
Generate static HTML versions in `notebooks/snapshots/` for users to view.

```bash
./make_snapshots.sh -s
# or for one notebook
./make_snapshots.sh -s notebooks/Polytope/feature_time_series.ipynb
```

---

## 3. Clear outputs before committing
Remove all outputs to keep notebooks clean for review.

```bash
./make_snapshots.sh -c
# or for one notebook
./make_snapshots.sh -c notebooks/Polytope/feature_time_series.ipynb
```
## 4. Update the list of notebooks in the README.md 
Update the list of notebooks in the README.md so others can easily find and reference the new or modified notebook.

---

## 5. Commit your changes
Add both the updated notebooks and their HTML snapshots, then push:

```bash
git add notebooks/snapshots notebooks/FDB notebooks/Polytope
git commit -m "Update notebooks and snapshots"
git push
```

---

> 💡 **Tip:**  
> - The script `make_snapshots.sh` can process all notebooks (default) or just a specific folder or file.  
> - Run `./make_snapshots.sh -h` for help.