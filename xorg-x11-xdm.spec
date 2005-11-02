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
# FIXME: Remove Epoch line if package gets renamed to something like "xdm"
Epoch: 1
Version: 0.99.2
Release: 1.20051031.2
License: MIT/X11
Group: User Interface/X
URL: http://www.x.org
Source0: %{pkgname}-%{version}-cvs20051031.tar.bz2
#Source0: %{pkgname}-%{version}.tar.bz2
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
# This file is for RHEL4/FC5 builds, which include the new audit system
Patch0: xdm-0.99.2-to-20051031.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# checking TMP_XAW_LIBS... -lXaw7 -lXmu -lXt -lSM -lICE -lXext -lXpm -lX11 -ldl
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
#Conflicts: 

# FIXME: The new audit system, required by xdm.pamd, was added to rawhide
# in pam-0.77-10.  If it is also present in an FC4 release, this part
# should be conditionalized to work on FC4 too.  (bug #159332)
#if %{build_fc5}
Requires: pam >= 0.77-10
#endif
#
###### OLD MONOLITHIC BUILD STUFF
# Don't think this is needed anymore, as it was a tie to the major X release.
#Requires: %{name} = %{version}
# NOTE: system-auth is part of the pam package itself, and has been there for a
# very long time now.  Since we wont be supporting systems that predate
# this with our modular packaging, this old monolithic rpm dep can just
# vanish.   I'll remove it at a later date.  <mharris>
#Requires: /etc/pam.d/system-auth
# pam requires were added for bug #159332 for new audit system.  It really
# should be a virtual provide in the pam package, to avoid odd version-release
# games, but this is the way it was done so we have to live with it.
#%if %{build_rhel4}
#Requires: pam >= 0.77-66.8
#%endif
# FIXME: xinitrc requirement on 3.13 for user login shell enhancement to
# Xsession, however modular X is probably going to Obsolete the xinitrc
# package, so this dependency should probably change to "xorg-x11-xinit"
# or whatever makes the most sense when we've figured it out.
#Requires: xinitrc >= 3.13
#######

%description
X.Org X11 xdm - X Display Manager

%prep
%setup -q -c %{name}-%{version}
#pushd %{pkgname}-%{version}
#%patch0 -p2 -b .to-20051031
#popd

%build
cd %{pkgname}-%{version}
%configure \
	--disable-static \
	--disable-xprint \
	--with-xdmconfigdir=%{_sysconfdir}/X11/xdm \
	--with-pixmapdir=%{_datadir}/xdm/pixmaps

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
cd %{pkgname}-%{version}
make install DESTDIR=$RPM_BUILD_ROOT

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find $RPM_BUILD_ROOT -name '*.la' | xargs rm -f --

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
   echo "FIXME: Upstream manpages install to incorrect location"
   mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1x
   for manpage in xdm ; do
      mv $RPM_BUILD_ROOT%{_mandir}/man1/$manpage.* $RPM_BUILD_ROOT%{_mandir}/man1x/$manpage.1x
   done
   rmdir $RPM_BUILD_ROOT%{_mandir}/man1
}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
{
  # FIXME:  I think we should disable this hack now, as I doubt anyone will
  # be upgrading from Red Hat Linux 6.2 or older to Fedora Core 5 directly,
  # and I'm not sure there is a large enough valid argument for us to support
  # that.  I'd rather remove the mess, than support such upgrades.  I will
  # leave it here for now however, rather than take a chance that it does
  # matter for newer OS release upgrades. -- mharris
  #
  # The dir /etc/X11/xdm/authdir moved to /var/lib/xdm/authdir and was replaced
  # by a symlink.  Upgrades from Red Hat Linux 6.x and earlier to any new
  # release with XFree86-4.0.x fail without the following. (fixes bug #32574)
  if [ ! -L /etc/X11/xdm/authdir -a -d /etc/X11/xdm/authdir ]; then
    mkdir -p /var/lib/xdm && \
    mv -f /etc/X11/xdm/authdir /var/lib/xdm/  && \
       ln -sf ../../../var/lib/xdm/authdir /etc/X11/xdm/authdir || :
  fi
} &> /dev/null || :

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
%{_sysconfdir}/X11/xdm/Xaccess
%{_sysconfdir}/X11/xdm/Xresources
%{_sysconfdir}/X11/xdm/Xservers
%{_sysconfdir}/X11/xdm/xdm-config
%{_sysconfdir}/pam.d/xdm
%{_sysconfdir}/pam.d/xserver
%dir %{_libdir}/X11
%dir %{_libdir}/X11/app-defaults
%{_libdir}/X11/app-defaults/Chooser
%dir %{_libdir}/X11/xdm
%{_libdir}/X11/xdm/GiveConsole
%{_libdir}/X11/xdm/TakeConsole
%{_libdir}/X11/xdm/Xreset
%{_libdir}/X11/xdm/Xsession
%{_libdir}/X11/xdm/Xsetup_0
%{_libdir}/X11/xdm/Xstartup
%{_libdir}/X11/xdm/Xwilling
%{_libdir}/X11/xdm/chooser
%{_libdir}/X11/xdm/libXdmGreet.so
%dir %{_mandir}
%dir %{_mandir}/man1x
%{_mandir}/man1x/*.1x*
%dir %{_datadir}/xdm
%dir %{_datadir}/xdm/pixmaps
%{_datadir}/xdm/pixmaps/xorg-bw.xpm
%{_datadir}/xdm/pixmaps/xorg.xpm

######################################################################
# FIXME:
# xorg-x11-6.8.99.14's file list for xdm, for developmental reference
# None of this stuff seems to be installed by current modularized xdm
# makefiles.  That probably indicates the upstream tarballs are broken
# and need fixing.  Having this here for reference will help us to fix
# the upstream tarballs and test it in rpm context.  Once it's all clean,
# this hideous mess can dissappear.  -- mharris
#%dir %{_sysconfdir}/X11/xdm
#%{_sysconfdir}/X11/xdm/authdir
#%dir %{_sysconfdir}/X11/xdm/pixmaps
#%{_sysconfdir}/X11/xdm/pixmaps/*
## We ship these in the xinitrc package
##%config /etc/X11/xdm/GiveConsole
##%config /etc/X11/xdm/TakeConsole
##%config /etc/X11/xdm/Xaccess
#%config /etc/X11/xdm/Xservers
## We ship these in the xinitrc package
##/etc/X11/xdm/Xsession
##/etc/X11/xdm/Xsetup_0
#%config /etc/X11/xdm/Xresources
#%config /etc/X11/xdm/Xwilling
## FIXME: chooser is an ELF executable, should not be in /etc really
#/etc/X11/xdm/chooser
#%config  %attr(0644,root,root) /etc/pam.d/xdm
#%{_x11bindir}/xdm
#%{_x11datadir}/X11/xdm
#%{_x11mandir}/man1/xdm.1*
#%dir /var/lib/xdm
#%dir %attr(0700,root,root) /var/lib/xdm/authdir
######################################################################

%changelog
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
