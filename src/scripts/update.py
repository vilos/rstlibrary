#!/usr/bin/env python
import sys, os
import svn.core, svn.client


def do_update(wc_path):
    # Build a client context baton.
    ctx = svn.client.svn_client_ctx_t()
        
    # Do the status crawl, using _status_callback() as our callback function.
    revision = svn.core.svn_opt_revision_t()
    revision.type = svn.core.svn_opt_revision_head

    msgs = svn.client.update(wc_path, revision, True, ctx)
    
    print msgs
    
def usage():
    
    print "Usage: %s  WC-PATH" % (os.path.basename(sys.argv[0]))
    
if __name__ == '__main__':
    
    args = sys.argv
    if len(args) <= 1:
        usage()
        
    # Canonicalize the repository path.
    wc_path = svn.core.svn_path_canonicalize(args[1])

    # Do the real work.
    try:
        do_update(wc_path)
    except svn.core.SubversionException, e:
        sys.stderr.write("Error (%d): %s\n" % (e.apr_err, e.message))
        sys.exit(1)