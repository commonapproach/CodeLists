#!/usr/bin/env sh
# This script runs in the Github CI environment. It sets up SSH access to the server,
# and rsync's the `public` folder into place.

# Create the .ssh directory on the runner. Used to store the ssh key for authentication
export SSHDIR="$HOME/.ssh"
mkdir -p "$SSHDIR"

# Copy the ssh key from the secrets store into the .ssh directory and assign the correct permissions
echo "$SSH_PRIVATE_KEY" > "$SSHDIR/key"
chmod 600 "$SSHDIR/key"

# Setup a variable to pass to ssh for the connection to the server. This
# includes the DOCROOT path to the public-facing web directory.
export SERVER_DEPLOY_STRING="$SSH_USERNAME@$SSH_SERVER:$SSH_DOCROOT"

# rsync everything to the documents location for the web server on my server 
/usr/bin/rsync -hlvcr --progress --delete --no-o --no-g -e "ssh -i $SSHDIR/key -o StrictHostKeyChecking=no" . "$SERVER_DEPLOY_STRING"
