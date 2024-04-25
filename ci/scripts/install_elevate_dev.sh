#!/usr/bin/env bash

USER='AlmaLinux'
BRANCH='almalinux'

show_usage() {
    echo 'Usage: sync_cloudlinux [OPTION]...'
    echo ''
    echo '  -h, --help           show this message and exit'
    echo '  -u, --user           github user name (default: AlmaLinux)'
    echo '  -b, --branch         github branch name (default: almalinux)'
}

while [[ $# -gt 0 ]]; do
    opt="$1"
    case ${opt} in
        -h|--help)
            show_usage
            exit 0
            ;;
        -u|--user)
            USER="$2"
            shift
            shift
            ;;
        -b|--branch)
            BRANCH="$2"
            shift
            shift
            ;;
        *)
            echo -e "Error: unknown option ${opt}" >&2
            exit 2
            ;;
    esac
done

RHEL_MAJOR_VERSION=$(rpm --eval %rhel)
WORK_DIR="$HOME"
NEW_LEAPP_NAME="leapp-repository-$BRANCH"
NEW_LEAPP_DIR="$WORK_DIR/$NEW_LEAPP_NAME/"
LEAPP_PATH='/usr/share/leapp-repository/repositories/'
LEAPP_GPG_PATH='/etc/leapp/repos.d/system_upgrade/common/files/rpm-gpg'
EXCLUDE_PATH='
/usr/share/leapp-repository/repositories/system_upgrade/el7toel8/files/bundled-rpms
/usr/share/leapp-repository/repositories/system_upgrade/el7toel8/files
/usr/share/leapp-repository/repositories/system_upgrade/el7toel8
/usr/share/leapp-repository/repositories/system_upgrade/el8toel9/files/bundled-rpms
/usr/share/leapp-repository/repositories/system_upgrade/el8toel9/files
/usr/share/leapp-repository/repositories/system_upgrade/el8toel9
/usr/share/leapp-repository/repositories/system_upgrade
/usr/share/leapp-repository/repositories/
'


echo "RHEL_MAJOR_VERSION=$RHEL_MAJOR_VERSION"
echo "WORK_DIR=$WORK_DIR"
echo "EXCLUDED_PATHS=$EXCLUDE_PATH"

echo "Preserve GPG keys if any"
for major in 8 9; do
    test -e ${LEAPP_GPG_PATH}/${major} && mv ${LEAPP_GPG_PATH}/${major} ${WORK_DIR}/
done


echo 'Remove old files'
for dir in $(find $LEAPP_PATH -type d);
do
    skip=0
    for exclude in $(echo $EXCLUDE_PATH);
    do
        if [[ $exclude == $dir ]];then
            skip=1
            break
        fi
    done
    if [ $skip -eq 0 ];then
        rm -rf $dir
    fi
done

echo "Download new tarball from https://github.com/$USER/leapp-repository/archive/$BRANCH/leapp-repository-$BRANCH.tar.gz"
curl -s -L https://github.com/$USER/leapp-repository/archive/$BRANCH/leapp-repository-$BRANCH.tar.gz | tar -xmz -C $WORK_DIR/ || exit 1

echo 'Deleting files as in spec file'
rm -rf $NEW_LEAPP_DIR/repos/common/actors/testactor
find $NEW_LEAPP_DIR/repos/common -name "test.py" -delete
rm -rf `find $NEW_LEAPP_DIR -name "tests" -type d`
find $NEW_LEAPP_DIR -name "Makefile" -delete
if [ $RHEL_MAJOR_VERSION -eq '7' ]; then
    rm -rf $NEW_LEAPP_DIR/repos/system_upgrade/el8toel9
else
    rm -rf $NEW_LEAPP_DIR/repos/system_upgrade/el7toel8
    rm -rf $NEW_LEAPP_DIR/repos/system_upgrade/cloudlinux
fi

echo 'Copy new data to system'
cp -r $NEW_LEAPP_DIR/repos/* $LEAPP_PATH || exit 1

for DIRECTORY in $(find $LEAPP_PATH -mindepth 1 -maxdepth 1 -type d);
do
    REPOSITORY=$(basename $DIRECTORY)
    if ! [ -e /etc/leapp/repos.d/$REPOSITORY ];then
        echo "Enabling repository $REPOSITORY"
        ln -s $LEAPP_PATH/$REPOSITORY /etc/leapp/repos.d/$REPOSITORY || exit 1
    fi
done

echo "Restore GPG keys if any"
for major in 8 9; do
    rm -rf ${LEAPP_GPG_PATH}/${major}
    test -e ${WORK_DIR}/${major} && mv ${WORK_DIR}/${major} ${LEAPP_GPG_PATH}/
done

rm -rf $NEW_LEAPP_DIR

exit 0
