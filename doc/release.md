# Release process

* Update `plpygis/_version.py`
* Update `CHANGELOG.md`
    - including footnotes
    - update date to release line
* Run `git push` and check CI for success
* Run `git tag vX.X.X`
* Run `git push origin vX.X.X`
* Run `python -m build`
* Run `twine upload dist/plpygis-X.X.X*`
* On https://github.com/bosth/plpygis/tags, create a release from the new tag
   - Use vX.X.X tag
   - Use vX.X.X as the title
   - Add a description of changes
   - Click "Generate release notes"
