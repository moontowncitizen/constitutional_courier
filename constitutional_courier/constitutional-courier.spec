Name:           constitutional-courier
Version:        1.0.0
Release:        1.0.1
Summary:        A GUI application to view the U.S. Constitution

License:        GPL v3
URL:            https://github.com/moontowncitizen/constitutional_courier
Source0:        constitutional-courier.tar.gz

BuildRequires:  python3-devel
Requires:       python3-gi, gtk4, gdk4

%description
Constitutional Courier is a GUI application built using Python and GTK4 that allows users to view the text of the U.S. Constitution.

%prep
%autosetup -n constitutional-courier

%build
%py3_build

%install
%py3_install

%files
%{_bindir}/constitutional-courier
%{python3_sitelib}/constitutional_courier
