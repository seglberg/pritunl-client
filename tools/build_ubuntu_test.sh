VERSION=`cat ../pritunl_client/__init__.py | grep __version__ | cut -d\' -f2`

gpg --import private_key.asc

mkdir -p ../build/debian_test
cd ../build/debian_test

wget https://github.com/pritunl/pritunl-client/archive/master.tar.gz

tar xfz master.tar.gz
mv pritunl-client-master pritunl-client-$VERSION
tar cfz $VERSION.tar.gz pritunl-client-$VERSION

tar xfz $VERSION.tar.gz
rm -rf pritunl-client-$VERSION/debian
tar cfz pritunl-client_$VERSION.orig.tar.gz pritunl-client-$VERSION
rm -rf pritunl-client-$VERSION

tar xfz $VERSION.tar.gz
cd pritunl-client-$VERSION

debuild
