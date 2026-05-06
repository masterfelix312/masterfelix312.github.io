---
layout: post
title: "OMV 8: Cannot Login to Workbench — Fix for Missing Salt State and passwd Error"
---

If you upgraded to or installed **OpenMediaVault 8** and suddenly cannot log into the web workbench, this post covers the three most common failure points and the exact steps to fix each one.

---

## Symptom 1 — `omv-salt deploy run omv.deploy.user` does not exist

Running the old OMV 6/7 reset procedure gives:

```
ERROR: The state 'omv.deploy.user' does not exist
```

**Why:** OMV 8 reorganised its Salt states. The `omv.deploy.user` module was removed; the web-admin password is now managed through OMV's configuration database, not through a Salt state.

**Fix:** Skip this command entirely and use `omv-firstaid` instead (see below).

---

## Symptom 2 — `passwd admin` returns "Authentication token manipulation error"

```
passwd: Authentication token manipulation error
passwd: password unchanged
```

This error means the kernel or filesystem is preventing writes to `/etc/shadow`. Common causes on OMV 8:

1. The root filesystem is mounted **read-only** (failing drive, fsck flag, or kernel panic recovery).
2. `/etc/shadow` has the **immutable attribute** set (`chattr +i`).
3. You are running `passwd` without root privileges.

**Diagnostics — run as root:**

```sh
# 1. Check filesystem mount flags
mount | grep ' / '
# Look for "ro" — if present the filesystem is read-only.

# 2. Check immutable flag on /etc/shadow
lsattr /etc/shadow
# If output starts with "----i---------", the file is immutable.

# 3. Confirm you are root
id
# uid=0(root) must be shown
```

**Fixes:**

```sh
# If /etc/shadow is immutable:
chattr -i /etc/shadow

# If the root filesystem is read-only, remount it read-write:
mount -o remount,rw /

# Then retry:
passwd admin
```

> **Important for OMV 8:** The `admin` Unix account password is *not* what protects the web workbench. Even after a successful `passwd admin` the web UI may still reject the old password. Always follow the OMV-native reset below as the final step.

---

## The correct OMV 8 web-admin password reset

### Option A — `omv-firstaid` (recommended)

```sh
sudo -i
omv-firstaid
```

In the menu select **"3 Reset web control panel password"** (the exact number may differ between releases). Enter the new password when prompted. Then restart services:

```sh
systemctl restart nginx
systemctl restart "php*-fpm" 2>/dev/null || true
systemctl restart openmediavault-engined
```

Open an **incognito/private** browser window, navigate to `http://<server-ip>/`, and log in with username `admin` and the password you just set.

### Option B — reset via `omv-confdbadm` (if `omv-firstaid` is unavailable)

```sh
sudo -i

# Read current web-admin configuration
omv-confdbadm read conf.system.webadmin
```

The output will show the current hashed password. To set a new one:

```sh
# Generate a SHA-512 hash of your new password
python3 -c "import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))"
```

Then open `/etc/openmediavault/config.xml`, find the `<webadmin>` section, and replace the value of `<password>` with the hash produced above. Apply the change:

```sh
omv-salt deploy run omv.deploy.nginx
omv-salt deploy run omv.deploy.phpfpm
systemctl restart openmediavault-engined
```

---

## Quick checklist

| Step | Command | Expected result |
|------|---------|-----------------|
| Become root | `sudo -i` | Prompt changes to `#` |
| Check filesystem RW | `mount | grep ' / '` | Contains `rw` |
| Remove immutable flag | `chattr -i /etc/shadow` | No error |
| Reset OMV web password | `omv-firstaid` | Password accepted |
| Restart services | `systemctl restart nginx openmediavault-engined` | Services start cleanly |
| Test login | Browser → `http://<ip>/` | Login succeeds |

---

If you still cannot log in after these steps, check the live logs while clicking Login in the browser:

```sh
journalctl -fu nginx &
journalctl -fu openmediavault-engined
```

The lines printed at the exact moment of the failed login will identify the remaining problem.
