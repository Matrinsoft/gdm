## START: Set by rpmautospec
## (rpmautospec version 0.8.4)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 2;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%global _hardened_build 1

# This controls support for launching X11 desktops.
# gdm itself will always use Wayland.
%if 0%{?rhel}
%bcond x11 0
%else
%bcond x11 1
%endif

Name:           gdm
Epoch:          1
Version:        51~rc
Release:        %autorelease
Summary:        The GNOME Display Manager

License:        GPL-2.0-or-later
URL:            https://wiki.gnome.org/Projects/GDM
Source0:        https://download.gnome.org/sources/%{name}/%{gnome_major_version}/%{name}-%{gnome_tarball_version}.tar.xz
Source1:        org.gnome.login-screen.gschema.override
Source2:        gdm.sysusers

%gnome_check_version

# Upstream patches

# Downstream patches
Patch:          0001-Honor-initial-setup-being-disabled-by-distro-install.patch
Patch:          0001-data-add-system-dconf-databases-to-gdm-profile.patch
Patch:          0001-Add-headless-session-files.patch

BuildRequires:  dconf
BuildRequires:  desktop-file-utils
BuildRequires:  gettext-devel
BuildRequires:  git-core
BuildRequires:  meson
BuildRequires:  pam-devel
BuildRequires:  pkgconfig(accountsservice) >= 0.6.3
BuildRequires:  pkgconfig(audit)
BuildRequires:  pkgconfig(check)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(gudev-1.0)
BuildRequires:  pkgconfig(iso-codes)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libkeyutils)
BuildRequires:  pkgconfig(libselinux)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(ply-boot-client)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(xau)
BuildRequires:  systemd-rpm-macros
BuildRequires:  which
BuildRequires:  yelp-tools

%if %{with x11}
BuildRequires:  pkgconfig(x11)
%endif

Provides: service(graphical-login) = %{name}

Requires: accountsservice
Requires: dbus-common
Requires: dconf
# since we use it, and pam spams the log if the module is missing
Requires: pam_oo7
Requires: gnome-session >= 50~alpha
Requires: gnome-session-wayland-session >= 50~alpha
Requires: gnome-settings-daemon >= 3.27.90
Requires: gnome-shell
Requires: iso-codes
# We need 1.0.4-5 since it lets us use "localhost" in auth cookies
Requires: libXau >= 1.0.4-4
Requires: pam
Requires: /sbin/nologin
Requires: systemd >= 186
Requires: system-logos
Requires: python3-pam

%if %{with x11}
Requires: xorg-x11-xinit
%endif

Provides: gdm-libs%{?_isa} = %{epoch}:%{version}-%{release}

%description
GDM, the GNOME Display Manager, handles authentication-related backend
functionality for logging in a user and unlocking the user's session after
it's been locked. GDM also provides functionality for initiating user-switching,
so more than one user can be logged in at the same time. It handles
graphical session registration with the system for both local and remote
sessions (in the latter case, via GNOME Remote Desktop and the RDP protocol).

%package devel
Summary: Development files for gdm
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: gdm-pam-extensions-devel = %{epoch}:%{version}-%{release}

%description devel
The gdm-devel package contains headers and other
files needed to build custom greeters.

%package pam-extensions-devel
Summary: Macros for developing GDM extensions to PAM
Requires: pam-devel

%description pam-extensions-devel
The gdm-pam-extensions-devel package contains headers and other
files that are helpful to PAM modules wishing to support
GDM specific authentication features.

%prep
%autosetup -S git -p1 -n %{name}-%{gnome_tarball_version}

%build
%meson -Ddbus-sys=%{_datadir}/dbus-1/system.d \
       -Ddefault-path=/usr/local/bin:/usr/bin \
       -Ddefault-pam-config=redhat \
       -Ddistro=redhat \
%if %{with x11}
       -Dx11-support=true \
%else
       -Dx11-support=false \
%endif

%meson_build

%install
%meson_install

cp -a %{SOURCE1} %{buildroot}%{_datadir}/glib-2.0/schemas

install -p -m644 -D %{SOURCE2} %{buildroot}%{_sysusersdir}/%{name}.conf

mkdir -p %{buildroot}%{_sysconfdir}/dconf/db/gdm.d/locks

%if %{with x11}
ln -sf ../X11/xinit/Xsession %{buildroot}%{_sysconfdir}/gdm/
%endif

%find_lang gdm --with-gnome

%post
%systemd_post gdm.service

%preun
%systemd_preun gdm.service

%postun
%systemd_postun gdm.service

%files -f gdm.lang
%doc AUTHORS NEWS README.md
%license COPYING
%dir %{_sysconfdir}/gdm
%config(noreplace) %{_sysconfdir}/gdm/custom.conf
%{_prefix}/lib/pam.d/gdm-autologin
%{_prefix}/lib/pam.d/gdm-password
%{_prefix}/lib/pam.d/gdm-password-auth-substack
# not config files
%if %{with x11}
%{_sysconfdir}/gdm/Xsession
%endif
%{_datadir}/gdm/gdm.schemas
%{_datadir}/dbus-1/system.d/gdm.conf
%dir %{_sysconfdir}/dconf/db/gdm.d
%dir %{_sysconfdir}/dconf/db/gdm.d/locks
%{_datadir}/glib-2.0/schemas/org.gnome.login-screen.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnome.login-screen.gschema.override
%{_libexecdir}/gdm-runtime-config
%{_libexecdir}/gdm-session-worker
%{_libexecdir}/gdm-new-session
%{_libexecdir}/gdm-wayland-session
%if %{with x11}
%{_libexecdir}/gdm-x-session
%endif
%{_libexecdir}/gdm-headless-login-session
%{_sbindir}/gdm
%{_bindir}/gdm-config
%dir %{_datadir}/dconf
%dir %{_datadir}/dconf/profile
%{_datadir}/dconf/profile/gdm
%dir %{_datadir}/gdm/greeter
%dir %{_datadir}/gdm/greeter/applications
%dir %{_datadir}/gdm/greeter/wayland-sessions
%{_datadir}/gdm/greeter/applications/*
%{_datadir}/gdm/greeter/wayland-sessions/*
%{_datadir}/gdm/greeter-dconf-defaults
%{_datadir}/gdm/locale.alias
%{_datadir}/gdm/gdb-cmd
%{_datadir}/gnome-session/sessions/gnome-login.session
%{_datadir}/polkit-1/rules.d/20-gdm.rules
%{_datadir}/polkit-1/actions/org.gnome.displaymanager.policy
%{_libdir}/girepository-1.0/Gdm-1.0.typelib
%{_libdir}/security/pam_gdm.so
%{_libdir}/libgdm.so.1{,.*}
%{_libexecdir}/gdm-auth-config-redhat
%ghost %dir %{_localstatedir}/log/gdm
%ghost %dir %{_localstatedir}/lib/gdm
%ghost %dir %{_rundir}/gdm
%{_prefix}/lib/pam.d/gdm-smartcard
%{_prefix}/lib/pam.d/gdm-smartcard-auth-substack
%{_prefix}/lib/pam.d/gdm-fingerprint
%{_prefix}/lib/pam.d/gdm-fingerprint-auth-substack
%{_prefix}/lib/pam.d/gdm-switchable-auth
%{_prefix}/lib/pam.d/gdm-switchable-auth-substack
%{_prefix}/lib/pam.d/gdm-launch-environment
%{_unitdir}/gdm.service
%{_unitdir}/gnome-headless-session@.service
%dir %{_userunitdir}/gnome-session@gnome-login.target.d/
%{_userunitdir}/gnome-session@gnome-login.target.d/gnome-login.session.conf
%{_sysusersdir}/%{name}.conf

%files devel
%dir %{_includedir}/gdm
%{_includedir}/gdm/*.h
%exclude %{_includedir}/gdm/gdm-pam-extensions.h
%exclude %{_includedir}/gdm/gdm-choice-list-pam-extension.h
%exclude %{_includedir}/gdm/gdm-custom-json-pam-extension.h
%exclude %{_includedir}/gdm/gdm-pam-extensions-common.h
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/Gdm-1.0.gir
%{_libdir}/libgdm.so
%{_libdir}/pkgconfig/gdm.pc

%files pam-extensions-devel
%{_includedir}/gdm/gdm-pam-extensions.h
%{_includedir}/gdm/gdm-choice-list-pam-extension.h
%{_includedir}/gdm/gdm-custom-json-pam-extension.h
%{_includedir}/gdm/gdm-pam-extensions-common.h
%{_libdir}/pkgconfig/gdm-pam-extensions.pc

%changelog
## START: Generated by rpmautospec
* Thu Sep 03 2026 Neal Gompa <ngompa@fedoraproject.org> - 1:51~rc-2
- Switch keyring dependency from gnome-keyring to oo7

* Wed Sep 02 2026 Milan Crha <mcrha@redhat.com> - 1:51~rc-1
- Update to 51.rc

* Wed Aug 05 2026 Jan Grulich <jgrulich@redhat.com> - 1:51~beta-1
- Update to 51.beta

* Wed Jul 15 2026 Fedora Release Engineering <releng@fedoraproject.org> - 1:51~alpha-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_45_Mass_Rebuild

* Wed Jul 01 2026 Milan Crha <mcrha@redhat.com> - 1:51~alpha-1
- Update to 51.alpha

* Fri May 29 2026 nmontero <nmontero@redhat.com> - 1:50.1-1
- Update to 50.1

* Mon May 11 2026 Michael Catanzaro <mcatanzaro@gnome.org> - 1:50.0-5
- Rebuild for accountsservice soname bump

* Tue Apr 07 2026 Jocelyn Falempe <jfalempe@redhat.com> - 1:50.0-4
- backport gdm.service.in: Also conflict with kmsconvt

* Wed Mar 25 2026 Jan Grulich <jgrulich@redhat.com> - 1:50.0-3
- Add configuration for release-monitoring

* Mon Mar 16 2026 Milan Crha <mcrha@redhat.com> - 1:50.0-1
- Update to 50.0

* Tue Mar 03 2026 Jan Grulich <jgrulich@redhat.com> - 1:50~rc-1
- Update to 50.rc

* Mon Mar 02 2026 Jan Grulich <jgrulich@redhat.com> - 1:50~beta-4
- Packit: drop upstream_project_url and rely on release-monitoring only

* Wed Feb 25 2026 Jan Grulich <jgrulich@redhat.com> - 1:50~beta-3
- Packit: drop fast_forward_merge_into as current stable branches diverge

* Tue Feb 24 2026 Jan Grulich <jgrulich@redhat.com> - 1:50~beta-2
- Onboard to Packit for stable Fedora branches

* Thu Feb 05 2026 Adam Williamson <awilliam@redhat.com> - 1:50~beta-1
- Update to 50~beta

* Thu Feb 05 2026 Adam Williamson <awilliam@redhat.com> - 1:50~alpha.1-4
- Backport MR #347 to fix startup on aarch64 VMs (and others)

* Tue Feb 03 2026 Jan Horak <jhorak@redhat.com> - 1:50~alpha.1-3
- Fix for local-display-factory: Fix display reference

* Tue Jan 20 2026 Jan Horak <jhorak@redhat.com> - 1:50~alpha.1-1
- Update to 50~alpha.1

* Fri Jan 16 2026 Fedora Release Engineering <releng@fedoraproject.org> - 1:49.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_44_Mass_Rebuild

* Thu Nov 27 2025 Debarshi Ray <rishi@fedoraproject.org> - 1:49.2-2
- Require gnome-session 49.beta

* Thu Nov 27 2025 Joan Torres Lopez <joantolo@redhat.com> - 1:49.2-1
- Update to 49.2

* Mon Nov 24 2025 Debarshi Ray <rishi@fedoraproject.org> - 1:49.1-5
- Restore 'Requires: xorg-x11-xinit'

* Mon Nov 24 2025 Fxzx micah <fxzxmicah@outlook.com> - 1:49.1-2
- Don't require dbus-daemon

* Fri Oct 10 2025 Packit <hello@packit.dev> - 1:49.1-1
- Update to 49.1 upstream release
- Resolves: rhbz#2403219

* Wed Sep 17 2025 Michael Catanzaro <mcatanzaro@redhat.com> - 1:49.0.1-6
- Also drop /usr/local/sbin from default path

* Wed Sep 17 2025 Jens Petersen <petersen@redhat.com> - 1:49.0.1-5
- drop deprecated /usr/sbin from the default PATH

* Wed Sep 17 2025 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1:49.0.1-4
- Drop call to %sysusers_create_compat

* Wed Sep 17 2025 Michael Catanzaro <mcatanzaro@redhat.com> - 1:49.0.1-3
- Simplify packaging

* Tue Sep 16 2025 Michael Catanzaro <mcatanzaro@redhat.com> - 1:49.0.1-2
- Restore X11 session support

* Tue Sep 16 2025 Michael Catanzaro <mcatanzaro@redhat.com> - 1:49.0.1-1
- Update to 49.0.1

* Thu Sep 04 2025 Michael Catanzaro <mcatanzaro@redhat.com> - 1:49~rc-1
- Update to 49.rc

* Tue Aug 12 2025 nmontero <nmontero@redhat.com> - 1:49~beta-1
- Update to 49~beta

* Wed Jul 23 2025 Fedora Release Engineering <releng@fedoraproject.org> - 1:49~alpha.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Mon Jul 07 2025 Milan Crha <mcrha@redhat.com> - 1:49~alpha.1-1
- Update to 49.alpha.1

* Tue Jun 17 2025 Carlos Garnacho <cgarnach@redhat.com> - 1:49~alpha.0-1
- Update to 49~alpha-0

* Sun May 18 2025 Michel Lind <salimma@fedoraproject.org> - 1:48.0-2
- Fix Source URL and make it easier to maintain

* Wed Mar 19 2025 nmontero <nmontero@redhat.com> - 1:48.0-1
- Update to 48.0

* Tue Feb 18 2025 nmontero <nmontero@redhat.com> - 1:48~beta-1
- Update to 48~beta

* Mon Jan 27 2025 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1:47.0-6
- Add patch to fix build with gcc 15 (rhbz#2340200)

* Thu Jan 16 2025 Fedora Release Engineering <releng@fedoraproject.org> - 1:47.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Fri Nov 22 2024 Davide Cavalca <dcavalca@fedoraproject.org> - 1:47.0-4
- Relocate dbus policy to /usr

* Tue Sep 17 2024 Ray Strode <rstrode@redhat.com> - 1:47.0-2
- Update sources

* Tue Sep 17 2024 Ray Strode <rstrode@redhat.com> - 1:47.0-1
- Update to 47.0, drop X11 support

* Mon Jul 22 2024 Ray Strode <rstrode@redhat.com> - 1:47~alpha-1
- Update to 47.alpha

* Thu Jul 18 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:46.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Thu Jul 11 2024 Niels De Graef <ndegraef@redhat.com> - 1:46.2-3
- Remove setxkbmap dependency

* Tue Jul 09 2024 Neal Gompa <ngompa@fedoraproject.org> - 1:46.2-2
- Drop rules for falling back in X11

* Thu May 30 2024 David King <amigadave@amigadave.com> - 1:46.2-1
- Update to 46.2

* Mon Apr 08 2024 Jonas Ådahl <jadahl@gmail.com> - 1:46.0-2
- Add headless session helper files

* Thu Mar 21 2024 David King <amigadave@amigadave.com> - 1:46.0-1
- Update to 46.0

* Fri Feb 02 2024 Stephen Gallagher <sgallagh@redhat.com> - 1:46.alpha-5
- Restore i686 on Fedora ELN

* Tue Jan 23 2024 Pavel Březina <pbrezina@redhat.com> - 1:46.alpha-4
- Add missing header files to gdm-pam-extensions-devel

* Fri Jan 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:46.alpha-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Wed Jan 17 2024 Michael Catanzaro <mcatanzaro@redhat.com> - 1:46.alpha-2
- Bump revision

* Wed Jan 17 2024 Michael Catanzaro <mcatanzaro@redhat.com> - 1:46.alpha-1
- Update to 46.alpha

* Wed Jan 17 2024 Yaakov Selkowitz <yselkowi@redhat.com> - 1:45.0.1-8
- Avoid Xorg build dependency

* Mon Jan 15 2024 Colin Walters <walters@verbum.org> - 1:45.0.1-7
- Scope ExcludeArch: ix86 to RHEL10+

* Tue Jan 09 2024 Troy Dawson <tdawson@redhat.com> - 1:45.0.1-6
- Exclude i686

* Thu Nov 30 2023 Yaakov Selkowitz <yselkowi@redhat.com> - 1:45.0.1-5
- Drop unused yelp-devel dependency

## END: Generated by rpmautospec
