pkgname=flasher
pkgver=1
pkgrel=1
pkgdesc="Flasher util to format or backup flash drive"
arch=('any')
license=('MIT')
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
