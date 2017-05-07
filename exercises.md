# Konténer techonlógiák laboratóriom

## Docker alapok

Ellenőrízze fut-e a docker démon, amennyeben nem indítsa el.

```bash
docker info  # fut-e a demon
sudo systemctl start docker  # demon inditasa
```

Legfontosabb parancs: `docker help`.

Töltsön le és indítson egy busybox-os konténert interaktív módban.
Majd irassa ki a rendszer informaciokat.
Ellenőrizze a konténerben az internet kapcsolattot.
Listáztassa ki a hálózati eszközöket.
Nézze meg a konténer ip címeit.
Lépjen ki a konténerből.

```bash
docker run -ti busybox
uname -a
ping -c1 8.8.8.8
ip link
ip address
exit
```

Jelenítse meg a futó konténereket.

```bash
docker ps
```

Indítson egy busybox konténert a `watch x` paranccsal, detach módban.
A konténer neve legyen x_watcher.

```bash
docker run --name x_watcher -d busybox watch x
```

Jelenítse meg ismét a futó konténereket.
Próbálja ki a `docker ps -a` parancsot.


Készítsen de ne futasson, egy busybox konténert ami folyamatosan pingeli a google dns szerverét.
Nevezze `ping_google`-nek.

```bash
docker create --name ping_google busybox ping 8.8.8.8
```

Listáztassa ki a konténereket a `docker ps -a` parancssal.

Jelenítsük meg a hosztgép hálózati eszközeit.

Vizsgáljuk meg a ping_google konténer beallításait.
```bash
docker inspect ping_google
```

Nézzük meg az x_watcher és a ping_google konténerek logjait.
```bash
docker logs x_watcher
docker logs ping_google
```

Vizsgáljuk meg a konténerekben futó folyamatokat is.
Tipp: docker top


## Volume-ok
Készítsünk egy data könyvtárat. Majd tegyünk bele néhány fájlt.
Ne feledjük a fájlok jogosultságait helyesen beállítani.

```bash
mkdir data
cd data
cat > data.txt <<EOF
Ez egy perzisztens adat.
EOF
chmod 777 data.txt
```

Indítsunk konténert volume-ként felcsatolva az elöbb létrehozott *data* könyvtárat,
a /data elérési út alá.
Módosítsuk nehány fájl tartalmát majd lépjünk ki a konténerből.

```bash
docker run -v $PWD:/data -ti ubuntu
```
Nezzük meg a fájl tartalmát.

Indítsunk konténert nevesített volume-ot létrehozva, vagy hozzunk létre nevesített volume-ot
és indítsunk konténert. A volume neve legyen *my_data* és csatoljuk /data alá.
Írjunk a /data-ba tetszőleges tartalmú fájlokat majd állítsuk le a konténert.
Ezután indítsunk egy az előzőtől eltérő image-ből konténert ugyanúgy felcsatolva a *my_data*
volume-ot.
Kukkantsunk be a /data-ba.

Egyik megoldás, első fele:
```bash
docker run -v my_data:/data -ti ubuntu
```

Masik megoldás, első fele:
```bash
docker volume create my_data
docker run -v my_data:/data -ti ubuntu
```

A megoldas masodik fele
```bash
docker run -v my_data:/data -ti centos
```

Indítsunk konténert névtelen volume-mal, a csatolási pont legyen az előzőkben
is használt /data. A konténert nevezzük *unnamed_volume*-nak.
Írjunk néhány fájlt /data-ba, majd zarjuk be a konténert.
Indítsunk egy másik konténert ugyanezzel a konfigurációval a konténer nevét leszámítva.
Nézzünk be a /data alá és ne szomorkodjunk.
Lépjünk ki majd indítsuk újra az *unnamed_volume* konténert, és látogassunk el a
/data-ba.

```bash
docker run -v /data --name unnamed_volume -ti ubuntu
docker run -v /data -ti ubuntu
docker start -ai unnamed_volume 
```

Nem csak könyvtárak lehetnek volume-ok, hanem fájlok is.
Csatoljuk be íras védett módban a /etc/passwd fájlt a /etc/passwd alá,
és állítsuk konténerben lévő user-t
*cloud*-ra.
A konténer indítása előtt és után is, adjuk ki a *whoami* illetve az *id* parancsot.

```bash
whoami
id
docker run -v /etc/passwd:/etc/passwd:ro --user cloud -ti ubuntu
whoami
id
```

Ha hibát tapasztalunk, akkor adjuk meg a *cloud* numerikus azonosítóját a neve helyett.
(Az id parancs ezt kiirja).
```bash
docker run -v /etc/passwd:/etc/passwd:ro --user `id -u` -ti ubuntu
```
Ne felejtsük futtatni a whoami és az id parancsokat.


## A konténer nem virtuális gép

A 3.10-es kernelben nem letező funkció.
Valami random ubuntus program ami ilyet hasznal.

Root image egyetelen statikusan linkelt programmal.

A programkód:
```c
#include <stdio.h>

int main(){
    printf(" Hello!\n I'm a static linked program in docker.\n");
    return 0;
}
```

Fordítás:
```bash
gcc -static -o hello hello.c
```

Archiválás és image készítés:
```bash
tar cvf hello.tar hello
docker image import hello.tar
```

Az importálás után megjelenik a letrehozott image azonosítója, ezt felhasználva
nevezzük át az image-t a `docker tag` parancs segítségével *static_hello*-ra.
Indítsunk egy static_hello konténert.
Ne felejtsük el megadni a futattandó program elérési utját!


## Dockerfile

Készítsünk Dockerfile-t, mely egy Nginx-et telepít.
Oldja meg hogy az összes modosítás csak egyetelen layer létrehozását eredményezze!
A weboldal tartalma a simple_nginx könyvtárban található.

```
# Nginx
#
# VERSION       1.0

FROM ubuntu
MAINTAINER okos hallgató

RUN apt update \
    && apt install -y nginx \
    && rm -f /var/www/html/index.nginx-debian.html

COPY simple_nginx/* /var/www/html

ENTRYPOINT /etc/init.d/nginx start
```

Probáljuk ki a Dockerfile-t, a keletkező image-ből indítsunk konténert.

```bash
cd simple_nginx
docker build .
docker tag XXX simple_nginx
```


