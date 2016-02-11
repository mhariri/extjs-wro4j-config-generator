ExtJS Wro4j Configuration Generator
===================================

In ExtJS, the dependencies of a class are defined in the following form:

    Ext.define('Mother', {
        requires: ['Child'],
        giveBirth: function() {
            // we can be sure that child class is available.
            return new Child();
        }
    });

And wro4j, in order to create a bundle of javascript files,
needs to know the order of putting the files in the bundle,
which is provided in its configuration file, ie wro.xml

This script will calculate the optimal load order for ExtJS
classes and gives the output in the wro4j config format.

The output can be copied into the specific portion of wro4j
configuration file.
