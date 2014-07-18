VERSION=`cat ../pritunl_client/__init__.py | grep __version__ | cut -d\' -f2`

gpg --import private_key.asc

mkdir -p /vagrant/build/debian
cd /vagrant/build/debian

wget https://github.com/pritunl/pritunl-client/archive/$VERSION.tar.gz

tar xfz $VERSION.tar.gz
rm -rf pritunl-client-$VERSION/debian
tar cfz pritunl-client_$VERSION.orig.tar.gz pritunl-client-$VERSION
rm -rf pritunl-client-$VERSION

tar xfz $VERSION.tar.gz
cd pritunl-client-$VERSION

debuild -S
sed -i -e 's/0ubuntu1/0ubuntu1~precise/g' debian/changelog
sed -i -e 's/trusty;/precise;/g' debian/changelog
debuild -S

cd ..

echo '\n\nRUN COMMANDS BELOW TO UPLOAD:'
echo 'sudo dput ppa:pritunl/ppa ../build/debian/pritunl-client_'$VERSION'-0ubuntu1_source.changes'
echo 'sudo dput ppa:pritunl/ppa ../build/debian/pritunl-client_'$VERSION'-0ubuntu1~precise_source.changes'
