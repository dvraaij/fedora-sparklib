# Upstream source information.
%global upstream_owner        AdaCore
%global upstream_name         SPARKlib
%global upstream_commit_date  20230801
%global upstream_commit       c2543114ce5ade62aad550e90de76f397804328f
%global upstream_shortcommit  %(c=%{upstream_commit}; echo ${c:0:7})

Name:           sparklib
Version:        0^%{upstream_commit_date}git%{upstream_shortcommit}
Release:        1%{?dist}
Summary:        SPARKlib, a collection of useful libraries in SPARK 2014
BuildArch:      noarch

License:        Apache-2.0 WITH LLVM-Exception

URL:            https://github.com/%{upstream_owner}/%{upstream_name}
Source:         %{url}/archive/%{upstream_commit}.tar.gz#/%{name}-%{upstream_shortcommit}.tar.gz

# [Fedora-specific] Remove scenario variables: values are fixed on Fedora.
Patch0:         %{name}-remove-scenario-vars.patch
# [Fedora-specific] Prepare insertion of the correct source file path during prep.
Patch1:         %{name}-prep-fix-paths.patch

BuildRequires:  /usr/bin/gnatprep
BuildRequires:  fedora-gnat-project-common

Recommends:     spark2014

# Build only on architectures where GPRbuild is available. The package is
# useless without GPRbuild, despite being architecture independent.
ExclusiveArch:  %{GPRbuild_arches}

%description

This package contains various libraries, such as a wide range of containers, as
well as lemmas to use directly in user code.

Please note that SPARKlib is used differently compared to how Ada libraries are
used. In short: if you want to use SPARKlib in your project, then, depending on
your runtime, copy either GPRbuild template "sparklib.gpr" or
"sparklib_light.gpr" from "%{_datadir}/%{name}/templates" to your own project
directory, edit the template (add an object directory, exclude source files that
are not needed in your project) and reference this local "sparklib.gpr" file in
your own project file.

See also section 5.11.1 SPARK Library in the SPARK user's manual (part
of package spark2014-doc) for details.


#############
## Prepare ##
#############

%prep
%autosetup -n %{upstream_name}-%{upstream_commit} p1

# Patch sparklib's hard-coded assumptions on (relative) paths.
# -- Note: Depends on the application of patch 1.
for gpr in *.gpr; do
    sed --in-place \
        --expression='s,@INCLUDEDIR@,%{_includedir},' \
        --expression='s,@NAME@,%{name},'              \
        $gpr
done

# Preprocess all files.
cd src
for f in *.ad{s,b}; do
    mv $f $f.in
    gnatprep -DSPARK_BODY_MODE=Off ${f}.in $f
    rm ${f}.in
done
cd -


###########
## Build ##
###########

%build
%nil


#############
## Install ##
#############

%install
%global inst install --mode=u=rw,go=r,a-s --preserve-timestamps
 
mkdir --parents %{buildroot}%{_GNAT_project_dir}
mkdir --parents %{buildroot}%{_includedir}/%{name}
mkdir --parents %{buildroot}%{_datadir}/%{name}/templates

# Install the invariant project files.
%{inst} --target-directory=%{buildroot}%{_GNAT_project_dir} ./sparklib_common.gpr
%{inst} --target-directory=%{buildroot}%{_GNAT_project_dir} ./sparklib_external.gpr
%{inst} --target-directory=%{buildroot}%{_GNAT_project_dir} ./sparklib_light_external.gpr

# Install the template project files that user's are supposed to copy into their local project.
%{inst} --target-directory=%{buildroot}%{_datadir}/%{name}/templates ./sparklib.gpr
%{inst} --target-directory=%{buildroot}%{_datadir}/%{name}/templates ./sparklib_light.gpr

# Install the source code.
%{inst} --target-directory=%{buildroot}%{_includedir}/%{name} ./src/*

# Show installed files (to ease debugging based on build server logs).
find %{buildroot} -exec stat --format "%A %n" {} \;


###########
## Files ##
###########

%files
%license LICENSE
%doc README*

%{_GNAT_project_dir}/%{name}*.gpr
%{_datadir}/%{name}
%{_includedir}/%{name}
# Exclude files that are used only when proving SPARKlib itself.
%exclude %{_includedir}/%{name}/spark-containers__exec.ads


###############
## Changelog ##
###############

%changelog
* Fri Aug 25 2023 Dennis van Raaij <dvraaij@fedoraproject.org> - 0^20230801gitc254311-1
- New package.
