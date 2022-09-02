from deptry.imports_to_package_names import ImportsToPackageNames

def test_simple_import():
    imported_modules = ['click']
    package_names = ImportsToPackageNames().convert(imported_modules)
    assert package_names == ['click']

def test_common_exception():
    imported_modules = ['bs4']
    package_names = ImportsToPackageNames().convert(imported_modules)
    assert package_names == ['beautifulsoup4']

def test_stdlib():
    imported_modules = ['sys']
    package_names = ImportsToPackageNames().convert(imported_modules)
    assert package_names == []