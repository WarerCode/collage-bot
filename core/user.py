"""

"""

import core.warerobjects.warerobject as warer
import core.warerobjects.politics.using_policy as using_policy
import core.warerobjects.data.userinfo as userinfo


class User(warer.WarerObject):
    """
    
    """
    
    def __init__(self,
                 info: userinfo.UserInfo,
                 policy: using_policy.UsingPolicy):
        """

        """
        super().__init__()
        self.info = info
        self.policy = policy



if __name__ == "__main__":
    pass
