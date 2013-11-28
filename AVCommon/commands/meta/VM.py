__author__ = 'zeno'

import logging
import time

from AVCommon import command

def execute(vm, args):
    """ client side, returns (bool,*) """
    logging.debug("    SET %s" % str(args))

    protocol, vms = args

    assert vm, "null vm"
    assert command.context is not None

    assert isinstance(vms, list), "VM expects a list"

    command.context["VM"] = vms


    logging.debug("items: %s" % (command.context))
    return True, "VM"