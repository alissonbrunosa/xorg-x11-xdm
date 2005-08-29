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
# FIXME: Upstream tarball is 0.99.0, which would require us to add an
# "Epoch: 1" to this package in order for rpm to upgrade from the FC4
# (and earlier) monolithic 6.8.x rpm package.  Since it is currently
# unknown what the final upstream tarball version is likely to be
# called, I am avoiding adding Epoch, and instead using a 6.99.99.x
# version number for the time being.  This allows us to make sure
# that it will upgrade from older releases to the new release, allows
# us to avoid adding an Epoch tag possibly unnecessarily - as Epoch
# is permanent and very evil.  If upstream later names it "<name>-7.0",
# then we bump the version to that, and everything just works.
%define upstreamversion 0.99.0

Summary: X.Org X11 xdm - X Display Manager
Name: xorg-x11-%{pkgname}
Version: 6.99.99.0
Release: 1
License: MIT/X11
Group: User Interface/X
URL: http://www.x.org
Source0: http://xorg.freedesktop.org/X11R7.0-RC0/everything/%{pkgname}-%{upstreamversion}.tar.bz2
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

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

# checking TMP_XAW_LIBS... -lXaw7 -lXmu -lXt -lSM -lICE -lXext -lXpm -lX11 -ldl
BuildRequires: xorg-x11-libXaw-devel
BuildRequires: xorg-x11-libXmu-devel
BuildRequires: xorg-x11-libXt-devel
BuildRequires: xorg-x11-libSM-devel
BuildRequires: xorg-x11-libICE-devel
BuildRequires: xorg-x11-libXext-devel
BuildRequires: xorg-x11-libXpm-devel
BuildRequires: xorg-x11-libX11-devel
# FIXME: There's no autotool dep on libXdmcp currently, but it fails with the
# following:
# configure: error: Library requirements (xdmcp) not met; consider adjusting
# the PKG_CONFIG_PATH environment variable if your libraries are in a
# nonstandard prefix so pkg-config can find them.
BuildRequires: xorg-x11-libXdmcp-devel
# FIXME: There's no autotool specified dep on this currently, but everything
# explodes looking for X11/Xauth.h without it:
BuildRequires: xorg-x11-libXau-devel

# FIXME: monolithic twm packaging has a hard dep on xterm, which might still
# be required.  We'll have to examine the twm configuration files.
#Requires: xterm
Provides: %{pkgname}
# FIXME: Ask on mailing list wether this virtual provide is remotely
# useful or not?
#Provides: displaywmanager
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

%build
cd %{pkgname}-%{upstreamversion}
%configure
make

%install
rm -rf $RPM_BUILD_ROOT
cd %{pkgname}-%{upstreamversion}
%makeinstall
# Install pam xdm config files
{
   mkdir -p $RPM_BUILD_ROOT%{_sysconfigdir}/pam.d
   install -c -m 644 %{SOURCE13} $RPM_BUILD_ROOT%{_sysconfigdir}/pam.d/xserver
# FIXME: I think the new audit system got released as an FC4 update, so
#        we might be able to remove this conditionalization, and just
#        use one xdm.pamd period.  In that case, FC3 and older users can
#        manually update to FC4 or later pam, or upgrade their whole OS
#        to something currently supported.
   if [ "%{build_fc3}" = "1" -o "%{build_fc4}" = "1" ] ; then
      install -c -m 644 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfigdir}/pam.d/xdm
   else
      install -c -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfigdir}/pam.d/xdm
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
# FIXME: Actually, xdm doesn't even install manpages at all by default for
# whatever reason.  That needs to be fixed prior to FC5.
%if 0
{
   echo "FIXME: Upstream manpages install to incorrect location"
   mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
   for manpage in xdm ; do
      mv $RPM_BUILD_ROOT%{_mandir}/manm/$manpage. $RPM_BUILD_ROOT%{_mandir}/man1/$manpage.1
   done
   rmdir $RPM_BUILD_ROOT%{_mandir}/manm
}
%endif
# FIXME: Upstream sources do not create the system wide xdm config dir, nor
# install the default config file currently.  We'll work around it here for now.
#{
#   echo "FIXME: Upstream doesn't install systemwide config by default"
#   mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/X11/xdm
#   install -m 0644 src/system.xdmrc $RPM_BUILD_ROOT%{_sysconfdir}/X11/xdm/
#}
   # FIXME: This is just copied over from monolithic spec file, to have
   # it in one place while making decisions, etc.  It will most likely be
   # removed entirely for the final builds, as we will likely move these
   # files back to the xdm package instead of keeping them in the xinitrc
   # package.  -- mharris
   # These are all present in our xinitrc package instead, however they
   # should move to the "xdm" package in modularized xorg, and conflict
   # should be set up with xinitrc packaging from older OS releases.  The
   # xinitrc package will need updating also. (old comment)
   %if 0
   {
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/GiveConsole
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/TakeConsole
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xaccess
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xsession
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xsetup_0
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xstartup
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xreset
      rm -f $RPM_BUILD_ROOT/etc/X11/xdm/xdm-config
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
%{_bindir}/chooser
%{_bindir}/sessreg
%{_bindir}/xdm
%{_bindir}/xdmshell
#%dir %{_mandir}
#%dir %{_mandir}/man1
#%{_mandir}/man1/xdm.1*

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
* Wed Aug 24 2005 Mike A. Harris <mharris@redhat.com> 0.99.0-1
- Initial build.
