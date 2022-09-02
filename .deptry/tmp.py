#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')
import toml
from pathlib import Path
import os
os.chdir('../../ppo/ppo-algorithm')


# In[ ]:


import sys
sys.path.append('/Users/florian.maas/git/ppo/ppo-algorithm/.venv/lib/python3.9/site-packages')


# In[ ]:


path_to_pyproject_toml = 'pyproject.toml'
path_to_venv = '.venv'
paths_to_ignore = ['.venv']


# In[ ]:


from deptry.core import Core
Core().run()


# In[ ]:


pyproject_text = Path("./pyproject.toml").read_text()
pyproject_data = toml.loads(pyproject_text)


# In[ ]:


pyproject_data['tool']['deptry']


# In[ ]:




