# Konténer technológiák laboratórium

Klónozzuk le a https://github.com/cemiarni/docker_labor.git repository-t.
Majd lépjünk a *docker_labor* könyvtárba, és végig dolgozzunk ott.
```bash
git clone https://github.com/cemiarni/docker_labor.git
cd labor_git
```

## Docker alapok

Ellenőrizzük fut-e a docker daemon, amennyiben nem indítsuk el.

```bash
docker info  # fut-e a demon
sudo systemctl start docker  # demon inditasa
```

Legfontosabb parancs: `docker help`.

Töltsük le és indítsunk egy busybox-os konténert interaktív módban.
Majd írassuk ki a rendszer információkat.
Ellenőrizzük a konténerben az internet kapcsolatot.
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
A konténer neve legyen *x_watcher*.

```bash
docker run --name x_watcher -d busybox watch x
```

Jelenítsük meg ismét a futó konténereket.
Próbáljuk ki a `docker ps -a` parancsot.


Készítsünk, de még ne futassuk, egy busybox konténert ami folyamatosan pingeli a google dns szerverét.
Nevezzük *ping_google*-nek.

```bash
docker create --name ping_google busybox ping 8.8.8.8
```

Listáztassuk ki a konténereket a `docker ps -a` parancssal.

Jelenítsük meg a hosztgép hálózati eszközeit.


Vizsgáljuk meg a *ping_google* konténer beállításait.
```bash
docker inspect ping_google
```
Indítsuk el a ping_google konténert. 

Nézzük meg az *x_watcher* és a *ping_google* konténerek logjait.
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

Indítsunk konténert volume-ként felcsatolva az előbb létrehozott *data* könyvtárat,
a /data elérési út alá.
Módosítsuk néhány fájl tartalmát majd lépjünk ki a konténerből.

```bash
docker run -v $PWD:/data -ti ubuntu
```
Nézzük meg a fájl tartalmát.

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

Másik megoldás, első fele:
```bash
docker volume create my_data
docker run -v my_data:/data -ti ubuntu
```

A megoldás második fele
```bash
docker run -v my_data:/data -ti centos
```

Indítsunk konténert névtelen volume-mal, a csatolási pont legyen az előzőkben
is használt /data. A konténert nevezzük *unnamed_volume*-nak.
Írjunk néhány fájlt /data-ba, majd zárjuk be a konténert.
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
Csatoljuk be írás védett módban a /etc/passwd fájlt a /etc/passwd alá,
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
(Az `id` parancs ezt kiírja).
```bash
docker run -v /etc/passwd:/etc/passwd:ro --user `id -u` -ti ubuntu
```
Ne felejtsük futtatni a `whoami` és az `id` parancsokat.


## A konténer nem virtuális gép

### Root image egyetlen statikusan linkelt programmal.

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

Az importálás után megjelenik a létrehozott image azonosítója, ezt felhasználva
nevezzük át az image-t a `docker tag` parancs segítségével *static_hello*-ra.
Indítsunk egy static_hello konténert.
Ne felejtsük el megadni a futtatandó program elérési útját!

### Kernel által nem támogatott funkció igénye a konténerben
Ritka eset de előfordulhat hogy konténerbe olyan szoftver kerül ami olyan
funkciót vár el a kerneltől amit nem támogat.
Konténer egyik előnye hogy hoszt rendszertől különböző linux disztribúciót
is futtathatunk a konténerben.
Sajnos előfordulhat hogy -- a disztribúciók mivel gyakran különböző verziójú és
konfigurációjú kernelt használnak -- egyes programok nem működnek.


## Dockerfile

Készítsünk Dockerfile-t, mely egy Nginx-et telepít.
A létrejövő image bázis image legyen az *ubuntu* nevű image.
A teszt weboldal tartalma a *simple_nginx* könyvtárban található,
ezt Dockerfile-ban másoljuk /var/www/http alá.
A másolást megelőzően töröljük le az alapértelmezett debian-os kezdőoldalt. 

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

Próbáljuk ki a Dockerfile-t, a keletkező image-ből indítsunk konténert.
A `-p` kapcsolóval tehetjük elérhetővé, azaz forward-olhatjuk a konténer
portjait a hosztgépnek címére. Ezt meg is tekinthetjük az `iptables` nat táblájának
`DOCKER` nevű chain-jében.

```bash
cd simple_nginx
docker build .
docker tag XXX simple_nginx
docker run -d -p80:80 simple_nginx
sudo iptables -t nat -L
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

Módosítsuk a Dockerfile-t: oldjuk meg hogy az nginx telepítés
és az alapértelmezett kezdő oldal törlése
csak egyetlen layer létrehozását eredményezze!
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

Egy egyszerű demonstráció setuid bittel ellátott program hosztrendszerre juttatása.
Készítsünk egy egyszerű c programot *reallywhoami* néven.
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
Fordítás és futtatás:
```bash
gcc -o reallywhoami reallywhoami.c
./reallywhoami
```
Jól láthatóan semmi különös. A laborgépek docker démonja úgy lett konfigurálva, hogy
használja a user namespace-t a konténereknél. Indítsunk egy konténert, csatoljuk be a /data
alá az aktuális munka könyvtárunkat, az indításkor adjuk meg a `--userns=host` kapcsolót
a user namespace kikapcsolásához.

A konténeren belül mivel root lesz a user-ünk,
vegyük birtokba a *reallywhoami* programot és aggassunk rá **setuid** bitet.
```bash
docker run --rm --userns=host -v $PWD:/data -ti ubuntu
cd /data
chown root  # tulajdonba vétel
chmod +s root  # setuid bit beállítása
```
Nyugodtan hagyjuk el a konténert és futtassuk újra a *reallywhoami* programot.
Hajjaj! Ugye ugye, a konténeren belüli root a hosztrendszeren is root.

Most töröljük le bináris és fordítsuk újra a programot. Ha futtatjuk, jól látszik, hogy
ismét helyreállt a rend.

![Docker Security artwork](security.png)

Indítsunk megint egy konténert úgy ahogy az előbb és játsszuk el amit az előbb, de
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
A könyvtárnak adjunk **777**-es jogot.
Majd lépjünk is be a könyvtárba.
```bash
mkdir build
cp reallywhoami reallywhoami.c build
chmod 777 build
cd build
```
Futtassuk a konténert az előbbi módon, majd belül másoljuk le a *reallywhoami* programot.
```bash
docker run --rm -v $PWD:/data -ti ubuntu
cd /data
cp reallywhoami reallywhoami2
```
Nézzük meg a *reallywhoami2* tulajdonosát.
Tegyük rá a *setuid* bitet.
Hagyjuk el a konténert és futtassuk a *reallywhoami2* programot.
Hát ilyenkor szomorkodnak egy pillanatra a hackerek.

Módosítsuk a c programot a következőre.
```c
#include<unistd.h>
#include<stdlib.h>

int main(){
    setuid(100000);
    system("whoami");
    return 0;
}
```
Töröljük a binárisokat fordítsuk újra a programot majd játsszuk el a konténeres trükköt.
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
Játsszuk el megint mint az előbb. A konténerből kilépés után futtassuk le *reallywhoami2*-t,
majd nézzük meg a *myfile* tulajdonosát.

Igen valóban sikerült egy másik user nevében futtatni de ha 100000 feletti user id-kat csak
a user namespace leképezéshez használjuk akkor, talán nem lehet vissza élni ezzel.

Mit csinál a user namespace? Mint ahogy az talán már az előbbieknél is látszott a konténeren
belüli user id-kat átképzi egy teljesen más user id-ra, a mi esetünkben hozzáad 100000-t.
Tehát konténeren belüli **X** userid a konténeren kívül a hoszt rendszeren valójában
a **100000+X** userid. Ez sajnos kihatással van a konténeren belüli műveletekre is
mint ahogy láttuk nem tudtuk tulajdonba venni a 100000 alatti uid-dal rendelkező
felhasználó fájljait, annak ellenére hogy a konténeren belül látszólag root-ként
tevékenykedtünk, szerencsére nem.


## Docker API

Készítsünk egy egyszerű webes megjelenítőt a futó konténereink listázására.
A megoldáshoz használjuk a docker python API-ját.

Lépjen be az *api_site* könyvtárba.
Futtassuk az `npm install` parancsot a kliens oldali függőségek telepítéséhez.
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
Az egyszerűség kedvéért az ezen vezérlési szerkezeteket használó kódrésszel már adottak.

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
A konténerhez tartozó összes attribútum az **attrs** tagváltozóban található,
kulcs-érték párok fájaként. 
A Jinja azonos szintaxissal támogatja a tagváltozók,
illetve a kulcs-érték párok hivatkozásait.
Az **attrs** tagváltozó tartalmának kiderítésében az [itt](https://docs.docker.com/engine/api/v1.28/#operation/ContainerInspect "Docker API - Inspect a container")
található oldal lehet segítségünkre.


### Konténerek metainformációi

A docker lehetőséget add az egyes objektumokhoz metainformációk **label**-ek rendeléséhez.
A label-ek kulcsérték párok, melyeket a konténerekre a következőképp aggathatunk.
```bash
docker run -l label1key=label1value --label label2key=label2value -ti busybox
```
A *--label-file* kapcsolóval egy fájlt is megadhatunk ami soronként tartalmazza
a kulcs-érték párokat.

A web site-unk megjeleníti a konténerek szám értékű címkéit.
A label-ek kulcsai megjelennek a konténer neve mellett, a kiemelési szín és 
a számérték közti leképezés a *main.py* **map_tag_label** függvényben található.

Próbáljuk ki!
Indítsunk néhány konténert különböző nevű és értékű label-ökkel.

Indítsunk konténert, hozzá adva az *owner* kulcsú label-t, érétkül pedig
adjunk meg a tulajdonos nevét.
Oldjuk meg hogy a konténer részleteinél megjelenjen a tulajdonos neve is.


## Swarm cluster

A következőekben egy Docker Swarm cluster-r fogunk összerakni.
Ehhez három gépre lesz szükségünk.
Az egyik amin eddig dolgoztunk, ezt nevezzuk *manager*-nek.
Célszerű a hosztnevét is átállítani a könnyebb tájékozódás érdekében.
A másik két gép a *worker1* és a *worker2*.

A manager gépen adjuk ki a következő parancsokat a docker démon swarm módba léptetéséhez.
```bash
sudo sh -c "echo manager >/etc/hostname"  # hosztnév beállítás első lépés
sudo hostname manager  # hosztnév beállítás mádosik lépés
docker swarm init --advertise-addr a_gep_ip_cime  # 'ip address' parancs segít
```
A manager gép ezennel manager üzemmódba lépett.
A megjelenő parancsot futtassuk a két worker gépen.
Ha minden jól sikerült akkor a következő üzenet fogad minket: *This node joined a swarm as a worker.*
Majd állítsuk be a workerek hosztneveit is.

A `docker info` paranccsal az eddigekhez képest plusz információkat kaphatunk a docker daemon-ról, mert most már
swarm módban van.

A cluster-ben lévő gépket és ezek állapotát a `docker node list` parancs segítségével tekinthetjük meg.

Az első service-ünk elkészítéséhez adjuk ki az alábbi parancsot, ami egy példányba indít konténert
valamely a cluster-ben résztvevő node-on.
```bash
docker service create --replicas 1 --name my_first_service busybox ping 8.8.8.8
```

A létrehozott service-ket a `docker service ls` paranccsal listáztathatjuk.
A service-kről többlet információt a `docker service inspect service_név` paranccsal kaphatunk..
A service-hez tartozó konténereket a `docker service ps service_név` kiadásával kapjuk,
ahol látszik a konténer neve, állapota és hogy melyik gépen fut.

Állítsuk a manager node-ot `DRAIN` állapotba, az az tiltsuk meg rajta a servicek általi konténer futtatást.
```bash
docker node update --availability drain manager
```

Nézzük meg a service-ünkhöz tartozó futó konténereket.
```bash
docker service ps my_first_service
```
A kimeneten jól látszik hogy manager-en leállt a konténer és elindult egy másik node-on.

Töröljük a service-ünket.
És ellenőrizzük hogy törlödtek-e a konténerek.
```bash
docker service rm my_first_service
```

Készítsünk egy service-t *replicated_service* néven.
Állítsuk be a replikációt 2-re és forward-oljuk a 80-as portot.
A swarm cluster automatikusan proxy-zza a kéréseinket a konténerek felé.
Konténerek használják a *simple_nginx* image-t!
```bash
docker service create \
  --name replicated_service \
  --publish 80:80 \
  --replicas 2 \
  simple_nginx
```
Sajnos nem indultak el konténereink, mivel az image csak a manager gépen létezik.
Ezt a tényt a `docker service ps replicated_service` kiadásával figyelhetjük meg.

Oldjuk meg a feladatot másképp: használjuk a Docker HUB-on elérhető *nginx* image-t.
Frissítsük az `update` alparanccsal a a service-t úgy hogy az említett image-t használja
és csatoljuk be a **simple_nginx** könyvtárat a */usr/share/nginx/html* elérési út alá
írásvédett módban.
Ez még sajnos nem elég a működéshez mert nincs mindegyik node-on a **simple_nginx** könyvtár.
Az egyszerűség kedvéért klónozzuk le minden node-ra a labor projektet.
Adjunk belepési jogot a home könyvtárba mindegyik node-on a `chmod 701 ~` kiadásával.

Most már futtathatjuk a service frissítést!
```bash
docker service update --image nginx --mount-add type=bind,src=/home/cloud/docker_labor/simple_nginx,dst=/usr/share/nginx/html,readonly replicated_service

docker ps replicated_service  # ellenőrizzük hogy elindult-e
```

**Kitérő**: a weboldal fájljainak megosztását szebben is meg lehetne oldani, ha mondjuk használunk valamilyen hálózati
megosztást a node-ok között.
Ez lehetne NFS megosztás, vagy minden node-ra felcsatolt Ceph RBD, vagy CephFS, stb.
Vagy használhatnánk ilyen megoldásokra épülő docker volume drivert is.
Az érdeklődők kedvükre válogathatnak [ebből](https://docs.docker.com/engine/extend/legacy_plugins/#volume-plugins "Docker Volume plugins")
a listából, vagy írhatnak saját driver-t.

A ellenőrizzük a böngészőben is, hogy mind a három node ip címén bejön-e a weboldal.
Hogy el is higgyük a manager gépen tényleg nem fut konténer futtassak mind három node-on
a `docker ps` parancsot.

### High Availability teszt

Nem várt leállást szimulálva altassuk le a *worker1* gépet.
Majd ellenőrizzük a weboldal elérését.
Egy kevés idő kellhet mire a Docker észbe kap, de utána látszik hogy kívülről tekintve helyreállt a rend.
A ha megnézzük a futó konténereket látszik hogy a *worker2*-ön két konténer fut.

Ébresszük fel a *worker1*-et és ellenőrizzük hogy elindult-e rajta a konténer.
Sajnos nem, de a `docker service update --force replicated_service` paranccsal újra tudjuk skálázni a rendszert.

Végezzük el újra a teljes tesztet úgy hogy előtte át állítjuk a service replikációját 1-re.

További információ a Docker Swarm-ról [itt](https://docs.docker.com/engine/swarm/ "Docker Swarm") található.


### Izolált hálózatok kitérő

Ha több ügyfelünk van és szeretnénk a az egyes ügyfelek hálózati forgalmát elszeparálni egymástól,
hogy az adott ügyfél csak a saját konténereivel tudjon kommunikálni, vagy ne tudja zavarni
más ügyfelek konténereit, akkor használhatunk overlay network-öt vagy Calico-t.

Az overlay network az előadáson bemutatott VXLAN megoldást használja a node-ok között.
A Calico szintén ismertetésre került az előadáson.


## Játék

Megérdemeljük a pihenést nézzünk meg egy youtube videót a dockercraft-ról,
ami futó konténereinket és róluk információkat vizualizál minecraft-ban.
Mind emellett pár művelet is elvégezhető a konténereken játék közben.

[![Dockercraft](http://img.youtube.com/vi/eZDlJgJf55o/0.jpg)](http://www.youtube.com/watch?v=eZDlJgJf55o "Youtube - Dockercraft")
A képre kattintás a youtube-ra navigál.
