# Maintainer: Alexandre Bury <alexandre.bury@gmail.com>
pkgname=flasher
pkgver=1
pkgrel=1
pkgdesc="Flasher util to format or backup flash drive"
depends=("parted" "systemd" "zstd")
optdepends=("exfat-utils: exfat backup support"
	    "btrfs-progs: btrfs backup support"
	    "ntfs-3g: ntfs backup support"
	    "hfsprogs: hfs backup support")
arch=('any')
license=('MIT')
install=flasher.install
source=("90-flasher.rules"
	"backup.sh"
	"flasher@.service"
	"format.sh"
	"install.sh"
	"main.sh")
sha256sums=("SKIP"
	    "SKIP"
	    "SKIP"
	    "SKIP"
	    "SKIP"
	    "SKIP")


package() {
	PREFIX=$pkgdir ./install.sh
}