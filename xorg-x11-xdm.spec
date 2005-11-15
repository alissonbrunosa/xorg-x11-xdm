# FIXME:  The modular xdm package still needs a fair bit of work, most
# of which probably needs to be done in the upstream CVS.  I've made
# numerous FIXME comments throughout to document things I think need
# to be done.  The spec file will naturally become less of a mess once
# the upstream tarball is kosher.  -- mharris

# The build_xxx macros are hopefully temporary.  I plan on removing them
# at some point in the near future anyway, when I have no personal use
# for them anymore, which probably is soon.  If anyone else is using them,
# I urge them to upgrade to FC5 ASAP.  ;o)
%define build_fc3	0
%define build_fc4	0

%define pkgname xdm

Summary: X.Org X11 xdm - X Display Manager
Name: xorg-x11-%{pkgname}
Version: 0.99.3
Release: 5
# NOTE: Remove Epoch line if package gets renamed to something like "xdm"
Epoch: 1
License: MIT/X11
Group: User Interface/X
URL: http://www.x.org
Source0: %{pkgname}-%{version}.tar.bz2
Source1: Xsetup_0
Source10: xdm.init
Source11: xdm.pamd
# FIXME: The xdm-pre-audit-system.pamd file is for FC3/FC4 builds, where
# the new audit system was not included in our pam implementation yet. I
# am not sure if FC4 has the new audit system, but if it does, this file
# will be removed as soon as I can confirm it, and the spec file will be
# useable only on FC4 and higher.  I leave this here for now only to make
# it easier to test modular X on more systems for personal convenience.
Source12: xdm-pre-audit-system.pamd
Source13: xserver.pamd
# NOTE: Change xdm-config to invoke Xwilling with "-s /bin/bash" instead
# of "-c" to fix bug (#86505)
Patch0: xdm-0.99.3-redhat-xdm-config-fix.patch
Patch1: xdm-0.99.3-xdm-configdir.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: libXaw-devel
BuildRequires: libXmu-devel
BuildRequires: libXt-devel
BuildRequires: libSM-devel
BuildRequires: libICE-devel
BuildRequires: libXext-devel
BuildRequires: libXpm-devel
BuildRequires: libX11-devel
# FIXME: There's no autotool dep on libXdmcp currently, but it fails with the
# following:
# configure: error: Library requirements (xdmcp) not met; consider adjusting
# the PKG_CONFIG_PATH environment variable if your libraries are in a
# nonstandard prefix so pkg-config can find them.
BuildRequires: libXdmcp-devel
# FIXME: There's no autotool specified dep on this currently, but everything
# explodes looking for X11/Xauth.h without it:
BuildRequires: libXau-devel

Provides: %{pkgname}
Obsoletes: XFree86-xdm
Obsoletes: xinitrc

# FIXME: check if still needed for X11R7
Requires(pre): filesystem >= 2.3.6-1

# FIXME: The new audit system, required by xdm.pamd, was added to rawhide
# in pam-0.77-10.  If it is also present in an FC4 release, this part
# should be conditionalized to work on FC4 too.  (bug #159332)
#if %{build_fc5}
Requires: pam >= 0.77-10
#endif

# pam requires were added for bug #159332 for new audit system.  It really
# should be a virtual provide in the pam package, to avoid odd version-release
# games, but this is the way it was done so we have to live with it.
#%if %{build_rhel4}
#Requires: pam >= 0.77-66.8
#%endif

%description
X.Org X11 xdm - X Display Manager

%prep
%setup -q -n %{pkgname}-%{version}
%patch0 -p0 -b .redhat-xdm-config-fix
%patch1 -p1 -b .xdmconfig

%build
#cd 
# FIXME: Work around pointer aliasing warnings from compiler for now
# resource.c:213: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:215: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:219: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:223: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:227: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:229: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:235: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:242: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:251: warning: dereferencing type-punned pointer will break strict-aliasing rules
# resource.c:253: warning: dereferencing type-punned pointer will break strict-aliasing rules

export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%configure \
	--disable-static \
	--disable-xprint \
	--with-xdmconfigdir=%{_sysconfdir}/X11/xdm \
	--with-pixmapdir=%{_datadir}/xdm/pixmaps

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find $RPM_BUILD_ROOT -name '*.la' | xargs rm -f --

install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xdm/Xsetup_0

# Install pam xdm config files
{
   mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
   install -c -m 644 %{SOURCE13} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/xserver
# FIXME: I think the new audit system got released as an FC4 update, so
#        we might be able to remove this conditionalization, and just
#        use one xdm.pamd period.  In that case, FC3 and older users can
#        manually update to FC4 or later pam, or upgrade their whole OS
#        to something currently supported.
   if [ "%{build_fc3}" = "1" -o "%{build_fc4}" = "1" ] ; then
      install -c -m 644 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/xdm
   else
      install -c -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/xdm
   fi
#   touch $RPM_BUILD_ROOT%{_sysconfigdir}/security/console.apps/xserver
}

# FIXME: This was in the monolithic xorg packaging, but I don't know if it
# is still needed.  If it is, it definitely should be fixed in upstream
# sources instead of cluttering the rpm build instructions.  <mharris>
# Explicitly create XDM authdir
#mkdir -m 700 -p $RPM_BUILD_ROOT/var/lib/xdm/authdir

# FIXME: Move manpages to correct man section and rename them.  This should
# get submitted as a bug upstream for each of the 4 components.  Hmm, the
# manpage(s) do not actually get installed.  Fix it and report it upstream.
%if 1
{
   echo "FIXME: Upstream RC2 manpages install to incorrect location"
   mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1x
   for manpage in xdm ; do
      mv $RPM_BUILD_ROOT%{_mandir}/man1/$manpage.* $RPM_BUILD_ROOT%{_mandir}/man1x/$manpage.1x
   done
   rmdir $RPM_BUILD_ROOT%{_mandir}/man1
}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
%dir %{_bindir}
#%dir %{_libdir}/xdm
#%{_libdir}/xdm/chooser
#%{_bindir}/sessreg
%{_bindir}/xdm
%{_bindir}/xdmshell
%dir %{_sysconfdir}/X11/xdm
# NOTE: The Xaccess file from our "xinitrc" package had no customizations,
# and was out of sync with upstream, so we ship the upstream one now.
%{_sysconfdir}/X11/xdm/Xaccess
%{_sysconfdir}/X11/xdm/Xresources
%{_sysconfdir}/X11/xdm/Xservers
%{_sysconfdir}/X11/xdm/xdm-config
# NOTE: In Fedora Core 4 and earlier, most of these config files and scripts
# were kept in the "xinitrc" package as forked copies, however they were
# quite out of date, and did not contain anything useful, so we now ship the
# upstream files and can patch them as needed to make changes.
%{_sysconfdir}/X11/xdm/GiveConsole
%{_sysconfdir}/X11/xdm/TakeConsole
%{_sysconfdir}/X11/xdm/Xreset
%{_sysconfdir}/X11/xdm/Xsession
%{_sysconfdir}/X11/xdm/Xsetup_0
%{_sysconfdir}/X11/xdm/Xstartup
%{_sysconfdir}/X11/xdm/Xwilling
%{_sysconfdir}/pam.d/xdm
%{_sysconfdir}/pam.d/xserver
# FIXME: app-defaults files should be in /usr/share
%dir %{_libdir}/X11
%dir %{_libdir}/X11/app-defaults
%{_libdir}/X11/app-defaults/Chooser
%dir %{_libdir}/X11/xdm
%{_libdir}/X11/xdm/chooser
%{_libdir}/X11/xdm/libXdmGreet.so
%dir %{_mandir}
%dir %{_mandir}/man1x
%{_mandir}/man1x/*.1x*
%dir %{_datadir}/xdm
%dir %{_datadir}/xdm/pixmaps
%{_datadir}/xdm/pixmaps/xorg-bw.xpm
%{_datadir}/xdm/pixmaps/xorg.xpm

%changelog
* Mon Nov 14 2005 Jeremy Katz <katzj@redhat.com> - 1:0.99.3-5
- require newer filesystem package (#172610)

* Mon Nov 14 2005 Jeremy Katz <katzj@redhat.com> - 1:0.99.3-4
- install scripts into /etc/X11/xdm instead of %%{_libdir} (#173081)
- use our Xsetup_0 instead of xorg one (#173083) 

* Sat Nov 12 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.3-3
- Added "Obsoletes: xinitrc", as xdm now provides files that were previously
  part of that package.  xorg-x11-xinit now provides the xinitrc scripts.

* Sat Nov 12 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.3-2
- Rebuild against new libXaw 0.99.2-2, which has fixed DT_SONAME.
- Added xdm-0.99.3-redhat-xdm-config-fix.patch which merges in an
  xdm-config fix present in the forked Red Hat xdm-config from the FC4
  xinitrc package, which invokes Xwilling with "-s /bin/bash" instead
  of "-c" to fix bug (#86505).
- Removed ancient xdm rpm preinstall script, as it should be unnecessary now.

* Fri Nov 11 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.3-1
- Update xdm to 0.99.3 from X11R7 RC2.

* Tue Nov 1 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.3
- Build with -fno-strict-aliasing to work around possible pointer aliasing
  issues

* Tue Nov 1 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.2
- It is _sysconfdir not _sysconfigdir goofball!
- Add {_sysconfdir}/pam.d/xdm and {_sysconfdir}/pam.d/xserver files that were
  missing from file manifest.

* Mon Oct 31 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.1
- Make sure all dirs are owned that xdm creates.
- Misc spec file cleanups

* Mon Oct 31 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.0
- Update xdm to 0.99.2 from X11R7 RC1.
- Update to CVS snapshot from 20051031
- Add Epoch 1, and change package to use the xdm version number.  Later, if
  we decide to rename the package to "xdm", we can drop the Epoch tag.
- Disable Xprint support
- Use _smp_mflags
- Add xdm-0.99.2-to-20051031.patch to pick up fixes from CVS head that allow
  us to set the config dir and other dirs.

* Wed Oct  5 2005 Mike A. Harris <mharris@redhat.com> 6.99.99.0-2
- Use Fedora-Extras style BuildRoot tag
- Update BuildRequires to use new library package names

* Wed Aug 24 2005 Mike A. Harris <mharris@redhat.com> 6.99.99.0-1
- Initial build.
