# mayaUnrealExporter

This tool is will provide an easy way to automatically export models, game ready rigs, and cameras into Unreal Engine 4

## Installation

Put the UnrealExporter folder and ueExport.py into your local Scripts directory for Maya.

If you do not have a custom path for your scripts, you can have them live under the C:\Users\userName\Documents\maya\mayaVersion\scripts folder

Shelf Button for Maya:

```
import ueExport
reload(ueExport)
ueExport.displayUI()
```
## Notes

* [Video Demo](https://vimeo.com/255215973)

* For skeletal mesh exports, the tool assumes that the rig that is exported is built for a Game Engine.
* For static mesh exports, the tool can only do one mesh at a time.
* For camera exports, what is recommended is importing the camera as a CineCameraActor within a Level Sequence
* The UnrealExport module has the capabilities of doing multiple asset exports.
* This tool has not been tested on the Unity engine, however the capability is possible with rigs and models.

## Built With
Maya 2017 Service Pack 4

Tested on Unreal Engine 4.17.2


## Authors
* **Greg Richardson** - [grichardson19](https://github.com/grichardson19)

## Acknowledgements

This was inspired from my time over at Halon Entertainment. I wrote this tool completely from scratch for my personal video game Heartwired.

Acknowledgements to:
* Micheal Oliver
* Nathan Dunsworth
* Casey Pyke
* Aaron Aikman
* Brian Magner