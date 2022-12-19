from typing import TypeVar

SuperglueJobType = TypeVar("SuperglueJobType", bound="SuperglueJob")
SuperglueModuleType = TypeVar("SuperglueModuleType", bound="SuperglueModule")
SuperglueComponentType = TypeVar("SuperglueComponentType", bound="SuperglueComponent")
SuperglueCommandType = TypeVar("SuperglueCommandType", bound="SuperglueCommand")
SuperglueMakefileType = TypeVar("SuperglueMakefileType", bound="SuperglueMakefile")
SuperglueTestsType = TypeVar("SuperglueTestsType", bound="SuperglueTests")
SuperglueFilesType = TypeVar("SuperglueFilesType", bound="SuperglueFiles")
