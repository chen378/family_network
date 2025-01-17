class node:
    def __init__(self,finger,asinfo=None,exit_policy=None,contact=None,alleged_family=None,effective_family=None,indirect_family=None):
        self.finger = finger
        self.asinfo = asinfo
        self.exit_policy = exit_policy
        self.contact = contact
        self.alleged_family = alleged_family
        self.effective_family = effective_family
        self.indirect_family = indirect_family