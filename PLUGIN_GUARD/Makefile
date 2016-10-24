#BRANCH=$(shell ../../script/rpm/getbranch.sh)
#VER_MAJ=$(shell ../../script/rpm/getver.sh | cut -d"." -f1)
#VER_MIN=$(shell ../../script/rpm/getver.sh | cut -d"." -f2| cut -d"-" -f1)
VER_PATCH=$(shell ../../script/rpm/getver.sh "v3.99" | cut -d"." -f2 | cut -d"-" -f2)
COMMIT_VER=$(shell ../../script/rpm/getver.sh "v3.99" | cut -d"." -f2 | cut -d"-" -f3)
REV=${VER_PATCH}.${COMMIT_VER}

__python=$(shell V=$$(python -V 2>&1 | awk '{ print $$2 }' | sed 's/\(.*\)\..*/\1/g'); if [[ "$$V" < '2.6' ]]; then echo 'python2.6'; else echo 'python$$PY'; fi)
__nosetests=$(shell which nosetests1.1 > /dev/null 2>&1 && echo nosetests1.1 || echo nosetests)
name=$(shell PYTHONPATH=. python -c 'import setup; print setup.PKG')
version=$(shell PYTHONPATH=. python -c 'import setup; print str(setup.META["__version__"])')
src=$(shell PYTHONPATH=. python -c 'import setup; print setup.SRC')


.PHONY: all
all: clean
	sed -i 's/^cover-package *=.*/cover-package = $(name)/' setup.cfg
	PYTHONPATH=. $(__python) setup.py develop -O1 --install-dir .
	# TODO: BuildRequires: and Requires: and... maybe the description from README...


.PHONY: sdist
sdist: all
	cp $(name).spec.in $(name).spec
#	sed -i 's|^Release:.*|Release:        ${REV}%{?dist}|g' ${name}.spec
#	sed -i 's|^Version:.*|Version:        ${version}|g' ${name}.spec
	PYTHONPATH=. $(__python) setup.py sdist
#	PYTHONPATH=. $(__python) setup.py bdist_rpm


.PHONY: bdist
bdist: all
	PYTHONPATH=. $(__python) setup.py bdist


.PHONY: rpm
rpm: sdist
	rm -rf ~/rpmbuild/SOURCES/$(name)*.tar.gz
	rm -rf ~/rpmbuild/RPMS/noarch/$(name)*.rpm
	rm -rf ~/rpmbuild/SRPMS/$(name)*.src.rpm
	cp dist/$(name)*.tar.gz ~/rpmbuild/SOURCES/
	rpmbuild -ba $(name).spec
	rm $(name).spec


.PHONY: test
test: all
	# PYTHONPATH=. $(__python) setup.py test
	# PYTHONPATH=. $(__python) setup.py nosetests
	PYTHONPATH=. $(__nosetests) -w $(src)


.PHONY: lint
lint:
	PYTHONPATH=. pylint $(name)
	# cd $(src) && pylint $(name)


.PHONY: doc
doc: all
	PYTHONPATH=. epydoc -o html --html -n 'pluginguard' --exclude=tests -v $(name)


.PHONY: userinstall
userinstall:
	PYTHONPATH=. $(__python) setup.py install --user --record=files.txt

.PHONY: uinst
uinst: userinstall


.PHONY: useruninstall
useruninstall: userinstall
	./uninstall.sh


.PHONY: uuninst
uuninst: useruninstall


.PHONY: clean
clean:
	PYTHONPATH=. $(__python) setup.py develop --uninstall --install-dir .
	rm -rf -- easy_install* $(src)/*.egg-info *.egg-link MANIFEST $(name).spec
	rm -rf -- .coverage build dist setuptools.pth site.py files.txt .tox
	find . -name '*.py[co]' -exec rm \{\} \;
	# Your custom binaries (console_scripts entry points)
	rm -f pluginguard_start pluginguard_status pluginguard_stop
	rm -rf pluginguard.egg-info 
	rm -rf html
