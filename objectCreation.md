#how creating of objects work (development style documentation)



there are 2 ways of creating a object:
  * creating by the interface
  * loading from a file
  * the current problem that may arise is that: when loading a light, and applying it onto a special node, that is not yet loaded the loader will not work.

my concept is to create the whole node-structure, and after this has been created applying special settings on them. that means that for every nodepath that is in the scene, there will be another nodepath-dummy. but i think that is bearable.

  * onCreateInstance is called when creating a object by the interface
  * loadFromEggGroup is called when loading the object
  * init creates a dummy (not any real content)
  * loadFromData actually calls the creator (not init, see the next line) of the object when loading
  * for example setModel in NodePathWrapper actually loads the model (this function may vary depending on the type of object)