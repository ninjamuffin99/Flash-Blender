bl_info = {
    "name": "Import Animate Spritesheet",
    "blender": (2, 83, 0),
    "category": "Object",
}

import bpy
from xml.etree import cElementTree as ElementTree
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

def insert_key(data, key, group=None):
    try:
        if group is not None:
            data.keyframe_insert(key, group=group)
        else:
            data.keyframe_insert(key)
    except:
        pass

def menu_func(self, context):
    self.layout.operator(ImportAnimateSpritesheet.bl_idname)

class ImportAnimateSpritesheet(Operator, ImportHelper):
    bl_idname = "animate.spritesheet_import"
    bl_label = "Import Animate Spritesheet"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context):
        
        cleanFile = bpy.path.display_name_from_filepath(self.filepath) + ".png"
        daImage = bpy.data.images.load(self.filepath, check_existing=True)
        
        if cleanFile in bpy.data.images:
            bpy.data.images[cleanFile].filepath = self.filepath
            bpy.ops.image.reload()
            print("IMAGE EXISTS!")
            
        print(self.filepath)
        imgWidth = daImage.size[0]
        imgHeight = daImage.size[1]

        xmlPath = self.filepath.replace('png', 'xml')
        print(xmlPath)
        bpy.data.texts.load(xmlPath.replace('C:\\', ''))
        xmlRoot = ElementTree.parse(xmlPath).getroot()
        
        
        scene = context.scene
        cursor = scene.cursor.location
        bpy.ops.mesh.primitive_plane_add(location=cursor)
        obj = bpy.context.object
        daFrame = scene.frame_current
        oldShit = [0, 0, 0, 0]
        
        
                    #0 = 0,0 / bottom left
                    #1 = 1,0 / bottom right
                    #2 = 1,1 / top right
                    #3 = 0,1 / top left
                    
        
        for element in xmlRoot:
            data = obj.data
            objectName = element.tag
            if 'x' in element.keys():
                
                uvX = float(element.get('x')) / imgWidth
                uvWidth = (float(element.get('width')) / imgWidth) + uvX
                uvY = float(element.get('y')) / imgHeight
                uvHeight = (float(element.get('height')) / imgHeight) + uvY
                
                newShit = [uvX, uvWidth, uvY, uvHeight]
                
                if oldShit != newShit:
                    pureWidth = float(element.get('width'))
                    pureHeight = float(element.get('height'))
                    
                    daRatio = 1
                    
                    if pureHeight > pureWidth:
                        daRatio = pureHeight / pureWidth
                    if pureWidth > pureHeight:
                        daRatio = pureWidth / pureHeight
                    
                    uvY*=-1
                    uvY+=1
                    uvHeight*=-1
                    uvHeight+=1
                    
                    obj.scale[0] = daRatio
                    # * self.da_scale
                    #obj.scale[1] = self.da_scale
                    obj.keyframe_insert(data_path='scale', index=-1, frame=daFrame)
                    #only applies with dynamic shit? where each frame could be different size?
                    #maybe an option of 'Trim'
                   
                    daUV = obj.data.uv_layers.active        
                    
                    daUV.data[0].uv[0] = uvX
                    daUV.data[1].uv[0] = uvWidth
                    daUV.data[2].uv[0] = uvWidth
                    daUV.data[3].uv[0] = uvX
                    
                    daUV.data[0].uv[1] = uvHeight
                    daUV.data[1].uv[1] = uvHeight
                    daUV.data[2].uv[1] = uvY
                    daUV.data[3].uv[1] = uvY
                    
                    ## IMPORTANT NOTE
                    ## DOES NOT ACCOUNT FOR THE 'frameWidth' OR 'frameHeight' variable!
                    ## Will probably cause issues if 'trimmed' is used when exporting the spritesheet
                    
                    for loop in obj.data.loops:
                        coolShit = obj.data.uv_layers.active.data[loop.index]
                        coolShit.keyframe_insert(data_path="uv", index=-1, frame=daFrame)
                
                #print( 'Attribute called TranslateX: {name}'.format(name=element.get('translateX')) )
                #locX = float(element.get('translateX'))
                #locY = float(element.get('translateY'))
                #locZ = float(element.get('translateZ'))
                #bpy.ops.mesh.primitive_monkey_add( location=(locX, locY, locZ) )
                oldShit = newShit
                
            daFrame+=1
        
        
        matName = "Spritesheet-"
        matName += bpy.path.display_name_from_filepath(daImage.filepath)
        
        ### IMAGE NODE SHIT
        ## Maybe you don't want this if/else???
        mat = bpy.data.materials.new(matName)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        principled = nodes.new("ShaderNodeBsdfPrincipled")
        mix = nodes.new("ShaderNodeMixShader")
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        matOutput = nodes.new("ShaderNodeOutputMaterial")
        node_imageTex = nodes.new(type="ShaderNodeTexImage")
     
        node_imageTex.image = daImage

        node_imageTex.location = -400,0
        principled.location = 0,-100
        mix.location = 300,0
        matOutput.location = 600,0


        links = mat.node_tree.links
        link = links.new(node_imageTex.outputs[0], principled.inputs[0])
        link2 = links.new(node_imageTex.outputs[1], mix.inputs[0])
        link3 = links.new(transparent.outputs[0], mix.inputs[1])
        link4 = links.new(principled.outputs[0], mix.inputs[2])
        link5 = links.new(mix.outputs[0], matOutput.inputs[0])
        
        obj.data.materials.append(mat)
        
        
        
        ## CHANGE INTERPOLATION MODE AND UPDATE ALL DA TWEEN SHIT
        area = bpy.context.area.type
        bpy.context.area.type = 'GRAPH_EDITOR'
        
        bpy.ops.graph.interpolation_type(type='CONSTANT')
        
        bpy.context.area.type = area
                
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ImportAnimateSpritesheet)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(ImportAnimateSpritesheet)


if __name__ == "__main__":
    register()
    
#MATH FOR TEXTURE/SCALING SHIT?
#set perfect square as reference point
#plane scales WITH 
#

