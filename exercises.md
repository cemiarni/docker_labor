# Konténer technológiák laboratórium

## Docker alapok

Ellenőrizzük fut-e a docker daemon, amennyiben nem indítsuk el.

```bash
docker info  # fut-e a demon
sudo systemctl start docker  # demon inditasa
```

Legfontosabb parancs: `docker help`.

Töltsük le és indítsunk egy busybox-os konténert interaktív módban.
Majd irassuk ki a rendszer informaciókat.
Ellenőrizzük a konténerben az internet kapcsolattot.
Listáztassuk ki a hálózati eszközöket.
Nézzük meg a konténer ip címeit.
Lépjünk ki a konténerből.

```bash
docker run -ti busybox
uname -a
ping -c1 8.8.8.8
ip link
ip address
exit
```

Jelenítsük meg a futó konténereket.

```bash
docker ps
```

Indítsunk egy busybox konténert a `watch x` paranccsal, detach módban.
A konténer neve legyen x_watcher.

```bash
docker run --name x_watcher -d busybox watch x
```

Jelenítsük meg ismét a futó konténereket.
Próbáljuk ki a `docker ps -a` parancsot.


Készítsünk de még ne futassuk, egy busybox konténert ami folyamatosan pingeli a google dns szerverét.
Nevezzük `ping_google`-nek.

```bash
docker create --name ping_google busybox ping 8.8.8.8
```

Listáztassuk ki a konténereket a `docker ps -a` parancssal.

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

Nézzük meg a konténerek statisztikáik a `docker stats`-val.
```bash
docker stats x_watcher
docker stats ping_google
```

Állítsuk le a *ping_google* konténert.


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
A konténer indítása előtt és után is, adjuk ki a `whoami` illetve az `id` parancsot.

```bash
whoami
id
docker run -v /etc/passwd:/etc/passwd:ro --user cloud -ti ubuntu
whoami
id
```

Ha hibát tapasztalunk, akkor adjuk meg a *cloud* numerikus azonosítóját a neve helyett.
(Az `id` parancs ezt kiirja).
```bash
docker run -v /etc/passwd:/etc/passwd:ro --user `id -u` -ti ubuntu
```
Ne felejtsük futtatni a `whoami` és az id parancsokat.


## A konténer nem virtuális gép

### Root image egyetelen statikusan linkelt programmal.

A programkód:
```c
/* static_hello.c */
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

### Kernel által nem támogatott funkció igénye a konténerben
Ritka eset de előfordulhat hogy konténerbe olyan szoftver kerül ami olyan
funkciót vár el a kerneltől amit nem támogat.
Konténer egyik előnye hogy hoszt rendszertől különböző linux disztribúciót
is futathatunk a konténberben.
Sajnos előfordulhat hogy -- a disztribúciók mivel gyakran különböző verziójú és
konfigurációjú kernelt használnak -- egyes programok nem működnek.


## Dockerfile

Készítsünk Dockerfile-t, mely egy Nginx-et telepít.
A létrejövő image bázis image legyen az *ubuntu* nevű image.
A teszt weboldal tartalma a *simple_nginx* könyvtárban található,
ezt Dockerfile-ban másoljuk /var/www/http alá.
A másolást megelőzően töröljük le az alapértelmezett debianos kezdőoldalt. 

A Dockerfile szintaxisáról a [itt](https://docs.docker.com/engine/reference/builder/ "Dockerfile reference")
találhatunk leírást.

Az egyszerűség kedvéért használjuk az alábbi kódot.
Amit a *simple_nginx* könyvtárban helyezzünk el **Dockerfile** néven.
```dockerfile
# Simple Nginx
#
# VERSION       1.0

FROM ubuntu
MAINTAINER okos hallgató

RUN apt update
RUN apt install -y nginx
RUN rm -f /var/www/html/index.nginx-debian.html

COPY index.html image.png /var/www/html/

ENTRYPOINT /usr/sbin/nginx -g "daemon off;"
```

Probáljuk ki a Dockerfile-t, a keletkező image-ből indítsunk konténert.

```bash
cd simple_nginx
docker build .
docker tag XXX simple_nginx
```

A konténer tesztelés után, a  `docker inspect` paranccsal vizsgáljuk meg az 
*ubuntu* image layer-eit.
Majd vizsgáljuk meg a *simple_nginx* image-ben is őket.
Hasonlítsuk össze a két listát.
```bash
docker image inspect ubuntu -f "{{range .RootFS.Layers}}{{.}} {{end}}" \
| tr ' ' '\n' \
| tee ubuntu_layers.txt

docker image inspect simple_nginx -f "{{range .RootFS.Layers}}{{.}} {{end}}" \
| tr ' ' '\n' \
| tee simple_nginx_layers.txt

diff ubuntu_layers.txt simple_nginx_layers.txt
```

Módosítsuk a Dockerfile-t: oldjuk meg hogy az összes lehetséges
módosítás csak egyetelen layer létrehozását eredményezze!
```dockerfile
# Simple Nginx
#
# VERSION       1.1

FROM ubuntu
MAINTAINER okos hallgató

RUN apt update \
    && apt install -y nginx \
    && rm -f /var/www/html/index.nginx-debian.html

COPY index.html image.png /var/www/html/

ENTRYPOINT /usr/sbin/nginx -g "daemon off;"

```
A generált image kapja a *simple_nginx2* nevet.

Az előzőleg használt módszerrel hasonlítsuk össze a *simple_nginx* és a *simple_nginx2*
image-k layer-eit.


## Biztonság

Ha konténereket kívánunk szolgáltatni az ügyfeleink számára akkor nagy figyelmet kell
szánunk a biztonsági beállításokra.
A konténerek a virtuális gépekkel szemben rengeteg sok elsőre nem is triviális biztonsági
rést rejtenek magukban.

Egy egyszerű demonstráció setuid bittel ellátott program hosztrandeszerre jutattása.
Készítsünk egy egyszerű c programot reallywhoami néven.
```c
/* reallywhoami.c */
#include<unistd.h>
#include<stdlib.h>

int main(){
    setuid(0);
    system("whoami");
    return 0;
}
```
Fordítás és futattás:
```bash
gcc -o reallywhoami reallywhoami.c
./reallywhoami
```
Jól láthatóan semmi különös. A laborgépek docker démonja úgy lett konfigurálva, hogy
használja a user namespace-t a konténereknél. Indítsunk egy konténert, csatoljuk be a /data
alá az aktuális munka könyvtárunkat, az indításkor adjuk meg a `--userns=host` kapcsolót
a user namespace kikapcsolásához.

A konténeren belül mivel root lesz a user-ünk,
vegyük birtokba a *reallywhoami* programot és aggasunk rá **setuid** bitet.
```bash
docker run --rm --userns=host -v $PWD:/data -ti ubuntu
cd /data
chown root  # tulajdonba vétel
chmod +s root  # setuid bit beállítása
```
Nyugottan hagyjuk el a konténert és futassuk újra a *reallywhoami* programot.
Hajajj! Ugye ugye, a konténeren belüli root a hosztrendszeren is root.

Most töröljük le bináris és fordítsuk újra a programot. Ha futatjuk, jól látszik, hogy
ismét helyreállt a rend.

Indítsunk megint egy konténert úgy ahogy az előbb és játszuk el amit az előbb, de
most ne használjuk a `--userns=host` kapcsolót.
```bash
docker run --rm -v $PWD:/data -ti ubuntu
cd /data
chown root
```
Ajha!
Nézzük meg a bináris és a /data könyvtár tulajdonosát: `ls -la`.
Nem ijedünk meg!
Lépjünk ki a konténerből.
Hozzunk létre könyvtárat *build* néven.
Másoljuk bele a kódot és a binárist.
A könyvtárnak adjunk 777-es jogot.
Majd lépjünk is be a könyvtárba.
```bash
mkdir build
cp reallywhoami reallywhoami.c build
chmod 777 build
cd build
```
Futassuk a konténert az előbbi módon, majd belül másoljuk le a *reallywhoami* programot.
```bash
docker run --rm -v $PWD:/data -ti ubuntu
cd /data
cp reallywhoami reallywhoami2
```
Nézzük meg a *reallywhoami2* tulajdonosát.
Tegyük rá a *setuid* bitet.
Hagyjuk el a konténert és futtasuk a *reallywhoami2* programot.
Hát ilyenkor szomorkodnak egy pillanatra a hackerek.

Módosítsuk a c porgramot a következőre.
```c
#include<unistd.h>
#include<stdlib.h>

int main(){
    setuid(100000);
    system("whoami");
    return 0;
}
```
Töröljük a binárisokat fordítsuk újra a programot majd jatszuk el a konténeres trükköt.
Látszólag nem változott semmi.

Módosítsuk ismét a programot:
```c
#include<unistd.h>
#include<stdlib.h>
#include<stdio.h>

int main(){
    setuid(100000);
    fopen("myfile", "w");
    return 0;
}
```
Játszuk el megint mint az előbb. A konténerből kilépés után futassuk le *reallywhoami2*-t,
majd nézzük meg a myfile tulajdonosát.

Igen valóban sikerült egy másik user nevében futatni de ha 100000 feletti user id-kat csak
a user namespace lekepézéshez használjuk akkor, talán nem lehet vissza élni ezzel.

Mit csinál a user namespace? Mint ahogy az talán már azlőbbieknél is látszott a konténeren
belüli user id-kat átképzi egy teljesen más user id-ra, a mi esetünkben hozzáad 100000-t.
Tehát konténeren belüli **X** userid a konténeren kívül a hoszt rendszeren valójában
a **100000+X** userid. Ez sajnos kihatással van a konténeren belülil műveletekre is
mint ahogy láttuk nem tudtuk tulajdonba venni a 100000 alatti uid-dal rendelkező
felhasználó fájljait, annak ellenére hogy a konténeren belül látszolag root-ként
tevékenykedtünk, szerencsére nem.


## Docker API

Készítsünk egy egyszerű webes megjelenitőt a futó konténereink listázására.
A megoldáshoz használjuk a docker python API-ját.

Lépjen be az *api_site* könyvtárba.
Futassuk az `npm install` parancsot a kliens oldali függőségek telepítéséhez.
Majd futtassuk a `sudo pip install -r requirements` parancsot a szerver oldali
függőségek telepítéséhez.
A web oldal váza már kész van.
Indítsuk el a fejlesztői szervert és tekintsük meg a félkész weboldalt a 8002-es porton.
Ezt a `python main.py` parancs kiadásával tehetjük meg.

A **main.py** fájl a webalkalmazás backned-je itt kell majd
elvégeznünk a docker API hívásokat.
A backend megvalósításához Flask web keretrendszert használjuk.

A templates könyvtárban található **container_list.html** egy Jinja template,
ebből fog generálódni a weboldal tartalma.
A *{{ }}* között kell megadnunk a változókat melyek értékéit látni szeretnénk a weboldalon.
A Jinja template a python szintaxisához hasonlóan támogat:
elágazásokat, ciklusokat, és függvény hívásokat.
Az egyszerűség kedvéért az ezen vezérlési szerkezeteket használó kódrészel már adottak.

### Feladat

Látogassunk el a docker python API dokumentációjához, [ide](https://docker-py.readthedocs.io/en/stable/ "Docker python API docs").

Töröljük ki a *main.py* **container_list** függvényéből a **Dummy** osztályt
és a **containers** listát.
Majd kérdezzük le az api segítségével a gépünkön található konténereket.
Az eredményt töltsük a **containers** változóba.
Frissítsük be a web oldalt, nézzük meg mi változott.

Módosítsuk a *templates* könyvtárban található *container_list.html* fájlt, 
találjuk meg és írjuk át a módosítandó részeket.

Sajnos a container objektumok nem tartalmaznak tagváltozóként minden attribútumot.
A konténerhez tartozó összes attribútum az **attrs** tagváltozóvban található,
kulcs-érték párok fájaként. 
A Jinja azonos szintaxissal támogatja a tagváltozok,
illetve a kulcs-érték párok hivatkozásait.
Az **attrs** tagváltozó tartalmának kiderítésében az [itt](https://docs.docker.com/engine/api/v1.28/#operation/ContainerInspect "Docker API - Inspect a container")
található oldal lehet segítségünkre.


### Konténerek metainformációi

A docker lehetőséget add az egyes objektumokhoz metainformációk **label**-ek rendereléséhez.
A label-ek kulcsérték párok, melyeket a konténerekre a következőképp aggathatunk.
```bash
docker run -l label1key=label1value --label label2key=label2value -ti busybox
```
A *--label-file* kapcsolóval egy fájlt is megadhatunk ami soronként tartalmazza
a kulcs-érték párokat.

A web site-unk megjelenití a konténerek szám értékű cimkéit.
A label-ek kulcsai megjelennek a konténer neve mellett, a kimelési szín és 
a számérték közti leképezés a *main.py* **map_tag_label** függvényben található.

Próbáljuk ki!
Indítsunk néhány konténert különböző nevű és értékű label-ökkel.

Indítsunk konténert, hozzá adva az *owner* kulcsú label-t, értkül pedig
adjunk meg a tulajdonos nevét.
Oldjuk meg hogy a konténer részleteinél megjelenjen a tulajdonos neve is.
