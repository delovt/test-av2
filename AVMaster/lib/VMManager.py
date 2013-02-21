import subprocess
import sys
import os

from ConfigParser import ConfigParser

class VMManagerVS:
	def __init__(self, config_file):
		self.config = ConfigParser()
		self.config.read(config_file)

		self.path = self.config.get("vsphere", "path")
		self.host = self.config.get("vsphere", "host")
		self.user = self.config.get("vsphere", "user")
		self.passwd = self.config.get("vsphere", "passwd")


	def _run_cmd(self, vmx, cmd, args=[], vmx_creds=[]):
		pargs = [   self.path,
					"-T", "vc",
					"-h", self.host,
					"-u", self.user, "-p", self.passwd, cmd, vmx.path ]
		if vmx_creds != [] and len(vmx_creds) == 2:
			idx = pargs.index("-p")+2
			cred = "-gu %s -gp %s" % ( vmx_creds[0], vmx_creds[1] )
			pargs = pargs[0:idx] + cred.split() + pargs[idx:]
			
		pargs.extend(args)
		subprocess.call(pargs)

	def startup(self, vmx):
		sys.stdout.write("[%s] Starting!\r\n" % vmx)
		self._run_cmd(vmx, "start")

	def shutdown(self, vmx):
		sys.stdout.write("[%s] Stopping!\r\n" % vmx)
		self._run_cmd(vmx, "stop")

	def reboot(self, vmx):
		sys.stdout.write("[%s] Rebooting!\r\n" % vmx)
		self._run_cmd(vmx, "reset", ["soft"])

	def suspend(self, vmx):
		sys.stdout.write("[%s] Suspending!\r\n" % vmx)
		self._run_cmd(vmx, "suspend", ["soft"])

	def createSnapshot(self, vmx, snapshot):
		sys.stdout.write("[%s] Creating snapshot %s.\n" % (vmx, vmx.snapshot))
		self._run_cmd(vmx, "snapshot", [snapshot])

	def deleteSnapshot(self, vmx, snapshot):
		sys.stdout.write("[%s] Deleting snapshot %s.\n" % (vmx, vmx.snapshot))
		self._run_cmd(vmx, "deleteSnapshot", [snapshot])

	def revertSnapshot(self, vmx, snapshot):
		sys.stdout.write("[%s] Reverting snapshot %s.\n" % (vmx, vmx.snapshot))
		self._run_cmd(vmx, "revertToSnapshot", [snapshot])

	def refreshSnapshot(self, vmx):
		sys.stdout.write("[%s] Refreshing snapshot %s.\n" % (vmx, vmx.snapshot))
		print "calling del"
		self.deleteSnapshot(vmx, vmx.snapshot)
		print "calling create"
		self.createSnapshot(vmx, vmx.snapshot)

	def mkdirInGuest(self, vmx, dir_path):
		sys.stdout.write("[%s] Creating directory %s.\n" % (vmx,dir_path))
		self._run_cmd(vmx, CreateDirectoryInGuest, [dir_path], [vmx.user,vmx.passwd])

	def copyFileToGuest(self, vmx, file_path = []):
		sys.stdout.write("[%s] Copying file from %s to %s.\n" % (vmx, src_file, dst_file))
		self._run_cmd(vmx, "CopyFileFromHostToGuest", file_path)

	def copyFileFromGuest(self, vmx, file_path = []):
		sys.stdout.write("[%s] Copying file from %s to %s.\n" % (vmx, src_file, dst_file))
		self._run_cmd(vmx, "CopyFileFromHostFromGuest", [file_path], [vmx.user, vmx.passwd])

	def executeCmd(self, vmx, cmd, args=[]):
		sys.stdout.write("[%s] Executing %s %s" % (vmx, cmd, str(args)))
		self._run_cmd(vmx, "runProgramInGuest", [cmd,args], [vmx.user, vmx.passwd])

	def takeScreenshot(self, vmx, out_img):
		sys.stdout.write("[%s] Taking screenshot.\n" % vmx)
		self._run_cmd(vmx, "captureScreen", [out_img], [vmx.user, vmx.passwd])


class VMManagerFus:
	def __init__(self, path):
		self.path = path

	def startup(self, vmx):
		sys.stdout.write("[*] Startup %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"start", vmx.path])
	
	def shutdown(self, vmx):
		sys.stdout.write("[*] Shutdown %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"stop", vmx.path])

	def reboot(self, vmx):
		sys.stdout.write("[*] Rebooting %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"reset", vmx.path, "soft"])

	def suspend(self, vmx):
		sys.stdout.write("[*] Suspending %s!\r\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"suspend", vmx.path, "soft"])

	def refreshSnapshot(self, vmx):
		sys.stdout.write("[*] Deleting current snapshot.\n")
		subprocess.call([self.path,
						"-T", "fusion",
						"deleteSnapshot", vmx.path, vmx.snapshot])
		sys.stdout.write("[*] Creating new snapshot %s for %s.\n" % (vmx.snapshot,vmx))
		subprocess.call([self.path,
						"-T", "fusion",
						"snapshot", vmx.path, vmx.snapshot])
						
	def revertSnapshot(self, vmx):
		sys.stdout.write("[*] Reverting %s to snapshot %s.\n" % (vmx, vmx.snapshot))
		subprocess.call([self.path,
						"-T", "fusion",
						"revertToSnapshot", vmx.path, vmx.snapshot])

	def copyFileToGuest(self, vmx, src_file, dst_file):
		sys.stdout.write("[*] Copying file %s to %s on %s.\n" % (src_file, dst_file, vmx))
		subprocess.call([self.path,
						"-T", "fusion",
						"CopyFileFromHostToGuest", vmx.path, src_file, dst_file])

	def executeCmd(self, vmx, cmd, script=None):
		if script is not None:
			sys.stdout.write("[*] Executing %s %s in %s.\r\n" % (cmd, script, vmx))
			proc = subprocess.call([self.path,
						"-T", "fusion",
						"-gu", vmx.user, "-gp", vmx.passwd,
						"runProgramInGuest", vmx.path, cmd, script])			
		else:
			sys.stdout.write("[*] Executing %s in %s.\r\n" % cmd, vmx)
			proc = subprocess.call([self.path,
						"-T", "fusion",
						"-gu", vmx.user, "-gp", vmx.passwd,
						"runProgramInGuest", vmx.path, cmd])
		if proc != 0:
			return False	
		return True			


	def takeScreenshot(self, vmx, out_img):
		sys.stdout.write("[*] Taking screenshot of %s.\n" % vmx)
		subprocess.call([self.path,
						"-T", "fusion",
						"-gu", vmx.user, "-gp", vmx.passwd,
						"captureScreen", vmx.path, out_img])
