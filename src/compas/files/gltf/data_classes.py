from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


class AlphaMode(object):
    BLEND = "BLEND"
    MASK = "MASK"
    OPAQUE = "OPAQUE"


class MineType(object):
    JPEG = "image/jpeg"
    PNG = "image/png"


# I changed the name of this so as not to collide with compas.Base
class BaseGLTFDataClass(object):

    IS_BASE_GLTF_DATA = True  # only needed for ipy in `GLTFContent.check_extensions_texture_recursively`

    def __init__(self, extras=None, extensions=None):
        self.extras = extras
        self.extensions = extensions

    def add_extension(self, extension):
        if not self.extensions:
            self.extensions = {}
        self.extensions.update({extension.key: extension})

    def extensions_to_data(self, **kwargs):
        if not self.extensions:
            return None
        return {key: value.to_data(**kwargs) if hasattr(value, "to_data") else value for key, value in self.extensions.items()}

    @classmethod
    def extensions_from_data(cls, data):
        # i hate hate hate this local import, but i don't see a good way around it
        from compas.files.gltf.extensions import SUPPORTED_EXTENSIONS

        if not data:
            return None
        extensions = {}
        for key, value_data in data.items():
            if key in SUPPORTED_EXTENSIONS:
                extensions[key] = SUPPORTED_EXTENSIONS[key].from_data(value_data)
            else:
                extensions[key] = value_data
        return extensions

    def to_data(self, *args, **kwargs):
        dct = {}
        if self.extras is not None:
            dct["extras"] = self.extras
        if self.extensions is not None:
            dct["extensions"] = self.extensions_to_data()
        return dct


class SamplerData(BaseGLTFDataClass):
    def __init__(
        self,
        mag_filter=None,
        min_filter=None,
        wrap_s=None,
        wrap_t=None,
        name=None,
        extras=None,
        extensions=None,
    ):
        super(SamplerData, self).__init__(extras, extensions)
        self.mag_filter = mag_filter
        self.min_filter = min_filter
        self.wrap_s = wrap_s
        self.wrap_t = wrap_t
        self.name = name

    def to_data(self):
        sampler_dict = {}
        if self.mag_filter is not None:
            sampler_dict["magFilter"] = self.mag_filter
        if self.min_filter is not None:
            sampler_dict["minFilter"] = self.min_filter
        if self.wrap_s is not None:
            sampler_dict["wrapS"] = self.wrap_s
        if self.wrap_t is not None:
            sampler_dict["wrapT"] = self.wrap_t
        if self.name is not None:
            sampler_dict["name"] = self.name
        if self.extras is not None:
            sampler_dict["extras"] = self.extras
        if self.extensions is not None:
            sampler_dict["extensions"] = self.extensions_to_data()
        return sampler_dict

    @classmethod
    def from_data(cls, sampler):
        if sampler is None:
            return None
        return cls(
            mag_filter=sampler.get("magFilter"),
            min_filter=sampler.get("minFilter"),
            wrap_s=sampler.get("wrapS"),
            wrap_t=sampler.get("wrapT"),
            name=sampler.get("name"),
            extras=sampler.get("extras"),
            extensions=cls.extensions_from_data(sampler.get("extensions")),
        )


class TextureData(BaseGLTFDataClass):
    def __init__(self, sampler=None, source=None, name=None, extras=None, extensions=None):
        super(TextureData, self).__init__(extras, extensions)
        self.sampler = sampler
        self.source = source
        self.name = name

    def to_data(self, sampler_index_by_key, image_index_by_key):
        texture_dict = {}
        if self.sampler is not None:
            texture_dict["sampler"] = sampler_index_by_key[self.sampler]
        if self.source is not None:
            texture_dict["source"] = image_index_by_key[self.source]
        if self.name is not None:
            texture_dict["name"] = self.name
        if self.extras is not None:
            texture_dict["extras"] = self.extras
        if self.extensions is not None:
            texture_dict["extensions"] = self.extensions_to_data()
        return texture_dict

    @classmethod
    def from_data(cls, texture):
        if texture is None:
            return None
        return cls(
            sampler=texture.get("sampler"),
            source=texture.get("source"),
            name=texture.get("name"),
            extras=texture.get("extras"),
            extensions=cls.extensions_from_data(texture.get("extensions")),
        )


class TextureInfoData(BaseGLTFDataClass):

    IS_TEXTURE_INFO_DATA = True  # only needed for ipy in `GLTFContent.check_extensions_texture_recursively`

    def __init__(self, index, tex_coord=None, extras=None, extensions=None):
        super(TextureInfoData, self).__init__(extras, extensions)
        self.index = index
        self.tex_coord = tex_coord

    def to_data(self, texture_index_by_key):
        texture_info_dict = {"index": texture_index_by_key[self.index]}
        if self.tex_coord is not None:
            texture_info_dict["texCoord"] = self.tex_coord
        if self.extras is not None:
            texture_info_dict["extras"] = self.extras
        if self.extensions is not None:
            texture_info_dict["extensions"] = self.extensions_to_data()
        return texture_info_dict

    @classmethod
    def from_data(cls, texture_info):
        if texture_info is None:
            return None
        return cls(
            index=texture_info["index"],
            tex_coord=texture_info.get("texCoord"),
            extras=texture_info.get("extras"),
            extensions=cls.extensions_from_data(texture_info.get("extensions")),
        )


class OcclusionTextureInfoData(TextureInfoData):
    def __init__(self, index, tex_coord=None, extras=None, extensions=None, strength=None):
        super(OcclusionTextureInfoData, self).__init__(index, tex_coord, extras, extensions)
        self.strength = strength

    def to_data(self, texture_index_by_key):
        texture_info_dict = super(OcclusionTextureInfoData, self).to_data(texture_index_by_key)
        if self.strength is not None:
            texture_info_dict["strength"] = self.strength
        return texture_info_dict

    @classmethod
    def from_data(cls, texture_info):
        if texture_info is None:
            return None
        return cls(
            index=texture_info["index"],
            tex_coord=texture_info.get("texCoord"),
            extras=texture_info.get("extras"),
            extensions=cls.extensions_from_data(texture_info.get("extensions")),
            strength=texture_info.get("strength"),
        )


class NormalTextureInfoData(TextureInfoData):
    def __init__(self, index, tex_coord=None, extras=None, extensions=None, scale=None):
        super(NormalTextureInfoData, self).__init__(index, tex_coord, extras, extensions)
        self.scale = scale

    def to_data(self, texture_index_by_key):
        texture_info_dict = super(NormalTextureInfoData, self).to_data(texture_index_by_key)
        if self.scale is not None:
            texture_info_dict["scale"] = self.scale
        return texture_info_dict

    @classmethod
    def from_data(cls, texture_info):
        if texture_info is None:
            return None
        return cls(
            index=texture_info["index"],
            tex_coord=texture_info.get("texCoord"),
            extras=texture_info.get("extras"),
            extensions=cls.extensions_from_data(texture_info.get("extensions")),
            scale=texture_info.get("scale"),
        )


class PBRMetallicRoughnessData(BaseGLTFDataClass):
    def __init__(
        self,
        base_color_factor=None,
        base_color_texture=None,
        metallic_factor=None,
        roughness_factor=None,
        metallic_roughness_texture=None,
        extras=None,
        extensions=None,
    ):
        super(PBRMetallicRoughnessData, self).__init__(extras, extensions)
        self.base_color_factor = base_color_factor
        self.base_color_texture = base_color_texture
        self.metallic_factor = metallic_factor
        self.roughness_factor = roughness_factor
        self.metallic_roughness_texture = metallic_roughness_texture

    def to_data(self, texture_index_by_key):
        roughness_dict = {}
        if self.base_color_factor is not None:
            roughness_dict["baseColorFactor"] = self.base_color_factor
        if self.base_color_texture is not None:
            roughness_dict["baseColorTexture"] = self.base_color_texture.to_data(texture_index_by_key)
        if self.metallic_factor is not None:
            roughness_dict["metallicFactor"] = self.metallic_factor
        if self.roughness_factor is not None:
            roughness_dict["roughnessFactor"] = self.roughness_factor
        if self.metallic_roughness_texture is not None:
            roughness_dict["metallicRoughnessTexture"] = self.metallic_roughness_texture.to_data(texture_index_by_key)
        if self.extras is not None:
            roughness_dict["extras"] = self.extras
        if self.extensions is not None:
            roughness_dict["extensions"] = self.extensions_to_data()
        return roughness_dict

    @classmethod
    def from_data(cls, texture_info):
        if texture_info is None:
            return None
        return cls(
            base_color_factor=texture_info.get("baseColorFactor"),
            base_color_texture=TextureInfoData.from_data(texture_info.get("baseColorTexture")),
            metallic_factor=texture_info.get("metallicFactor"),
            roughness_factor=texture_info.get("roughnessFactor"),
            metallic_roughness_texture=TextureInfoData.from_data(texture_info.get("metallicRoughnessTexture")),
            extras=texture_info.get("extras"),
            extensions=cls.extensions_from_data(texture_info.get("extensions")),
        )


class MaterialData(BaseGLTFDataClass):
    def __init__(
        self,
        name=None,
        extras=None,
        pbr_metallic_roughness=None,  # PBRMetallicRoughnessData
        normal_texture=None,  # NormalTextureInfoData
        occlusion_texture=None,  # OcclusionTextureInfoData
        emissive_texture=None,  # TextureInfoData
        emissive_factor=None,
        alpha_mode=None,
        alpha_cutoff=None,
        double_sided=None,
        extensions=None,
    ):
        super(MaterialData, self).__init__(extras, extensions)
        self.name = name
        self.pbr_metallic_roughness = pbr_metallic_roughness
        self.normal_texture = normal_texture
        self.occlusion_texture = occlusion_texture
        self.emissive_texture = emissive_texture
        self.emissive_factor = emissive_factor
        self.alpha_mode = alpha_mode
        self.alpha_cutoff = alpha_cutoff
        self.double_sided = double_sided

    def to_data(self, texture_index_by_key):
        material_dict = {}
        if self.name is not None:
            material_dict["name"] = self.name
        if self.extras is not None:
            material_dict["extras"] = self.extras
        if self.pbr_metallic_roughness is not None:
            material_dict["pbrMetallicRoughness"] = self.pbr_metallic_roughness.to_data(texture_index_by_key)
        if self.normal_texture is not None:
            material_dict["normalTexture"] = self.normal_texture.to_data(texture_index_by_key)
        if self.occlusion_texture is not None:
            material_dict["materialTexture"] = self.occlusion_texture.to_data(texture_index_by_key)
        if self.emissive_texture is not None:
            material_dict["emissiveTexture"] = self.emissive_texture.to_data(texture_index_by_key)
        if self.emissive_factor is not None:
            material_dict["emissiveFactor"] = self.emissive_factor
        if self.alpha_mode is not None:
            material_dict["alphaMode"] = self.alpha_mode
        if self.alpha_cutoff is not None:
            material_dict["alphaFactor"] = self.alpha_cutoff
        if self.double_sided is not None:
            material_dict["doubleSided"] = self.double_sided
        if self.extensions is not None:
            material_dict["extensions"] = self.extensions_to_data(texture_index_by_key=texture_index_by_key)
        return material_dict

    @classmethod
    def from_data(cls, material):
        if material is None:
            return None
        return cls(
            name=material.get("name"),
            extras=material.get("extras"),
            pbr_metallic_roughness=PBRMetallicRoughnessData.from_data(material.get("pbrMetallicRoughness")),
            normal_texture=NormalTextureInfoData.from_data(material.get("normalTexture")),
            occlusion_texture=OcclusionTextureInfoData.from_data(material.get("occlusionTexture")),
            emissive_texture=TextureInfoData.from_data(material.get("emissiveTexture")),
            emissive_factor=material.get("emissiveFactor"),
            alpha_mode=material.get("alphaMode"),
            alpha_cutoff=material.get("alphaCutoff"),
            double_sided=material.get("doubleSided"),
            extensions=cls.extensions_from_data(material.get("extensions")),
        )


class CameraData(BaseGLTFDataClass):
    def __init__(
        self,
        type_,
        orthographic=None,
        perspective=None,
        name=None,
        extras=None,
        extensions=None,
    ):
        super(CameraData, self).__init__(extras, extensions)
        self.type = type_
        self.orthographic = orthographic
        self.perspective = perspective
        self.name = name

    def to_data(self):
        camera_dict = {"type": self.type}
        if self.orthographic is not None:
            camera_dict["orthographic"] = self.orthographic
        if self.perspective is not None:
            camera_dict["perspective"] = self.perspective
        if self.name is not None:
            camera_dict["name"] = self.name
        if self.extras is not None:
            camera_dict["extras"] = self.extras
        if self.extensions is not None:
            camera_dict["extensions"] = self.extensions_to_data()
        return camera_dict

    @classmethod
    def from_data(cls, camera):
        if camera is None:
            return None
        return cls(
            type_=camera["type"],
            orthographic=camera.get("orthographic"),
            perspective=camera.get("perspective"),
            name=camera.get("name"),
            extras=camera.get("extras"),
            extensions=cls.extensions_from_data(camera.get("extensions")),
        )


class AnimationSamplerData(BaseGLTFDataClass):
    def __init__(self, input_, output, interpolation=None, extras=None, extensions=None):
        super(AnimationSamplerData, self).__init__(extras, extensions)
        self.input = input_
        self.output = output
        self.interpolation = interpolation

    def to_data(self, input_accessor, output_accessor):
        sampler_dict = {
            "input": input_accessor,
            "output": output_accessor,
        }
        if self.interpolation is not None:
            sampler_dict["interpolation"] = self.interpolation
        if self.extras is not None:
            sampler_dict["extras"] = self.extras
        if self.extensions is not None:
            sampler_dict["extensions"] = self.extensions_to_data()
        return sampler_dict

    @classmethod
    def from_data(cls, sampler, input_, output):
        if sampler is None:
            return None
        return cls(
            input_=input_,
            output=output,
            interpolation=sampler.get("interpolation"),
            extras=sampler.get("extras"),
            extensions=cls.extensions_from_data(sampler.get("extensions")),
        )


class TargetData(BaseGLTFDataClass):
    def __init__(self, path, node=None, extras=None, extensions=None):
        super(TargetData, self).__init__(extras, extensions)
        self.path = path
        self.node = node

    def to_data(self, node_index_by_key):
        target_dict = {"path": self.path}
        if self.node is not None:
            target_dict["node"] = node_index_by_key[self.node]
        if self.extras is not None:
            target_dict["extras"] = self.extras
        if self.extensions is not None:
            target_dict["extensions"] = self.extensions_to_data()
        return target_dict

    @classmethod
    def from_data(cls, target):
        if target is None:
            return None
        return cls(
            path=target["path"],
            node=target.get("node"),
            extras=target.get("extras"),
            extensions=cls.extensions_from_data(target.get("extensions")),
        )


class ChannelData(BaseGLTFDataClass):
    def __init__(self, sampler, target, extras=None, extensions=None):
        super(ChannelData, self).__init__(extras, extensions)
        self.sampler = sampler
        self.target = target

    def to_data(self, node_index_by_key, sampler_index_by_key):
        channel_dict = {
            "sampler": sampler_index_by_key[self.sampler],
            "target": self.target.to_data(node_index_by_key),
        }
        if self.extras is not None:
            channel_dict["extras"] = self.extras
        if self.extensions is not None:
            channel_dict["extensions"] = self.extensions_to_data()
        return channel_dict

    @classmethod
    def from_data(cls, channel):
        if channel is None:
            return None
        return cls(
            sampler=channel["sampler"],
            target=TargetData.from_data(channel["target"]),
            extras=channel.get("extras"),
            extensions=cls.extensions_from_data(channel.get("extensions")),
        )


class AnimationData(BaseGLTFDataClass):
    def __init__(self, channels, samplers_dict, name=None, extras=None, extensions=None):
        super(AnimationData, self).__init__(extras, extensions)
        self.channels = channels
        self.samplers_dict = samplers_dict
        self.name = name

        self._sampler_index_by_key = None

    def to_data(self, samplers_list, node_index_by_key):
        channels = [channel_data.to_data(node_index_by_key, self._sampler_index_by_key) for channel_data in self.channels]
        animation_dict = {
            "channels": channels,
            "samplers": samplers_list,
        }
        if self.name is not None:
            animation_dict["name"] = self.name
        if self.extras is not None:
            animation_dict["extras"] = self.extras
        if self.extensions is not None:
            animation_dict["extensions"] = self.extensions_to_data()
        return animation_dict

    def get_sampler_index_by_key(self):
        self._sampler_index_by_key = {key: index for index, key in enumerate(self.samplers_dict)}
        return self._sampler_index_by_key

    @classmethod
    def from_data(cls, animation, channel_data_list, sampler_dict):
        if animation is None:
            return None
        return cls(
            channels=channel_data_list,
            samplers_dict=sampler_dict,
            name=animation.get("name"),
            extras=animation.get("extras"),
            extensions=cls.extensions_from_data(animation.get("extensions")),
        )


class SkinData(BaseGLTFDataClass):
    def __init__(
        self,
        joints,
        inverse_bind_matrices=None,
        skeleton=None,
        name=None,
        extras=None,
        extensions=None,
    ):
        super(SkinData, self).__init__(extras, extensions)
        self.joints = joints
        self.inverse_bind_matrices = inverse_bind_matrices
        self.skeleton = skeleton
        self.name = name

    def to_data(self, node_index_by_key, accessor_index):
        node_indices = [node_index_by_key.get(item) for item in self.joints if node_index_by_key.get(item) is not None]
        skin_dict = {"joints": node_indices}
        if self.skeleton is not None:
            skin_dict["skeleton"] = self.skeleton
        if self.name is not None:
            skin_dict["name"] = self.name
        if self.extras is not None:
            skin_dict["extras"] = self.extras
        if self.inverse_bind_matrices is not None:
            skin_dict["inverseBindMatrices"] = accessor_index
        if self.extensions is not None:
            skin_dict["extensions"] = self.extensions_from_data()
        return skin_dict

    @classmethod
    def from_data(cls, skin, inverse_bind_matrices):
        if skin is None:
            return None
        return cls(
            joints=skin["joints"],
            inverse_bind_matrices=inverse_bind_matrices,
            skeleton=skin.get("skeleton"),
            name=skin.get("name"),
            extras=skin.get("extras"),
            extensions=cls.extensions_from_data(skin.get("extensions")),
        )


class ImageData(BaseGLTFDataClass):
    def __init__(
        self,
        data=None,
        uri=None,
        mime_type=None,
        name=None,
        extras=None,
        extensions=None,
    ):
        super(ImageData, self).__init__(extras, extensions)
        self.uri = uri
        self.mime_type = mime_type
        self.name = name
        self.data = data

    def to_data(self, uri, buffer_view):
        image_dict = {}
        if self.name is not None:
            image_dict["name"] = self.name
        if self.extras is not None:
            image_dict["extras"] = self.extras
        if self.mime_type is not None:
            image_dict["mimeType"] = self.mime_type
        if uri is not None:
            image_dict["uri"] = uri
        elif buffer_view is not None:
            image_dict["bufferView"] = buffer_view
        elif self.uri is not None:
            image_dict["uri"] = self.uri
        if self.extensions is not None:
            image_dict["extensions"] = self.extensions_from_data()
        return image_dict

    @classmethod
    def from_data(cls, image, data, mime_type):
        if image is None:
            return None
        return cls(
            uri=image.get("uri"),
            mime_type=image.get("mimeType") or mime_type,
            name=image.get("name"),
            extras=image.get("extras"),
            extensions=cls.extensions_from_data(image.get("extensions")),
            data=data,
        )


class PrimitiveData(BaseGLTFDataClass):
    def __init__(
        self,
        attributes,
        indices=None,
        material=None,
        mode=None,
        targets=None,
        extras=None,
        extensions=None,
    ):
        super(PrimitiveData, self).__init__(extras, extensions)
        self.attributes = attributes or {}
        self.indices = indices
        self.material = material
        self.mode = mode
        self.targets = targets

    def to_data(self, indices_accessor, attributes_dict, targets_dict, material_index_by_key):
        primitive_dict = {"indices": indices_accessor}
        if self.material is not None:
            primitive_dict["material"] = material_index_by_key[self.material]
        if self.mode is not None:
            primitive_dict["mode"] = self.mode
        if self.extras is not None:
            primitive_dict["extras"] = self.extras
        if attributes_dict:
            primitive_dict["attributes"] = attributes_dict
        if targets_dict:
            primitive_dict["targets"] = targets_dict
        if self.extensions is not None:
            primitive_dict["extensions"] = self.extensions_to_data()
        return primitive_dict

    @classmethod
    def from_data(cls, primitive, attributes, indices, target_list):
        if primitive is None:
            return None
        return cls(
            attributes=attributes,
            indices=indices,
            material=primitive.get("material"),
            mode=primitive.get("mode"),
            targets=target_list,
            extras=primitive.get("extras"),
            extensions=cls.extensions_from_data(primitive.get("extensions")),
        )
