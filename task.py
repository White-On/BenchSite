"""Docstring for task.py module.

This module contains the class Task and the differents function to manipulate the Task class.

"""

from dataclasses import dataclass, field
from typing import ClassVar
import numpy as np
from logger import logger


@dataclass
class Task:
    """
    Store all the information about all the tasks created.

    Attributes
    ----------
    name : str
        The name of the task.
    theme : str
        The theme of the task.
    arguments : list of float
        The list of the arguments of the task. The index of the argument correspond to the index of the result.
    results : list of float
        The list of the results of the task. The index of the result correspond to the index of the argument.
    allTasks : list of Task
        Class Atribute ! The list of all the tasks created.

    """

    name: str
    theme: str
    arguments: list[float] = field(default_factory=list)
    runtime: dict[str, list[float]] = field(default_factory=dict)
    evaluation: dict[str, list[float]] = field(default_factory=dict)
    arguments_label: list[str] = field(default_factory=list)
    cache_runtime: dict[str, list[float]] = field(default_factory=dict)
    cache_evaluation: dict[str, list[float]] = field(default_factory=dict)
    allTasks: ClassVar[list["Task"]] = []

    def __post_init__(self) -> None:
        logger.debug(f"Task {self.name} created")
        Task.allTasks.append(self)

    def __repr__(self) -> str:
        return f"Task({self.name})-> arguments: {self.arguments_label}"

    @classmethod
    def GetAllTask(cls) -> list["Task"]:
        """Getter for all the tasks created.

        Returns
        -------
        list of Task
            The list of all the tasks created.

        """
        return cls.allTasks

    @classmethod
    def GetAllTaskName(cls) -> list[str]:
        """Getter for all the tasks name created.

        Returns
        -------
        listtaskName : list of str
            The list of all the tasks name created.

        """
        listTaskName = []
        for task in cls.allTasks:
            if task.name not in listTaskName:
                listTaskName.append(task.name)
        return listTaskName

    @classmethod
    def GetTaskByName(cls, taskName: str) -> "Task" or None:
        """Getter for a task by its name.

        Parameters
        ----------
        taskName : str
            The name of the task to get.

        Returns
        -------
        task : Task
            The task with the name given in parameter.

        """
        for task in cls.allTasks:
            if task.name == taskName:
                return task
        return None

    @classmethod
    def GetAllTaskByName(cls, taskName: str):
        """Getter for all the tasks with the same name.

        Parameters
        ----------
        taskName : str
            The name of the task to get.

        Returns
        -------
        list of Task
            The list of all the tasks with the same name.

        """
        return (task for task in cls.allTasks if task.name == taskName)

    @classmethod
    def GetAllThemeName(cls):
        """Getter for all the theme name created.

        Returns
        -------
        listThemeName : list of str
            The list of all the theme name created.

        """
        listThemeName = []
        for task in cls.GetAllTask():
            if task.theme not in listThemeName:
                listThemeName.append(task.theme)
        return listThemeName

    @classmethod
    def GetTaskByThemeName(cls, themeName: str):
        """Getter for all the tasks with the same theme name.

        Parameters
        ----------
        themeName : str
            The name of the theme to get.

        Returns
        -------
        list of Task
            The list of all the tasks with the same theme name.

        """
        return (task for task in cls.GetAllTask() if task.theme == themeName)

    @classmethod
    def GetTaskNameByThemeName(cls, themeName: str) -> list[str]:
        """Getter for all the tasks name with the same theme name.

        Parameters
        ----------
        themeName : str
            The name of the theme to get.

        Returns
        -------
        list of str
            The list of all the tasks name with the same theme name.

        """
        listTaskName = []
        for task in cls.GetTaskByThemeName(themeName):
            if task.name not in listTaskName:
                listTaskName.append(task.name)
        return listTaskName

    # @staticmethod
    # def transform_str_to_nan(array: np.ndarray) -> np.ndarray:
    #     def is_float(string: str):
    #         try:
    #             float(string)
    #             return True
    #         except ValueError:
    #             return False

    #     array[np.vectorize(lambda x: not is_float(x))(array)] = np.nan
    #     array = array.astype(np.float64)
    #     return array

    @staticmethod
    def str_and_none_to_nan(array: np.ndarray) -> np.ndarray:
        """transform the string and None into np.nan and transform the array into float64"""

        def is_float(string: str):
            """return True if the string is a float, False otherwise"""
            try:
                float(string)
                return True
            except ValueError:
                return False

        return np.where(
            np.vectorize(lambda x: x is None or not is_float(x))(array), np.nan, array
        ).astype(np.float64)

    def get_runtime(self, target: str) -> list[float]:
        # we transform the string and None into np.nan and transform the array into float64
        runtime = Task.str_and_none_to_nan(np.array(self.runtime[target]))
        # if there is no runtime for the target, we return a list of np.nan with the same size as the arguments
        if (np.isnan(runtime)).all():
            return np.vstack(runtime).tolist()
        # we inverse the runtime to have the difference between the end and the start
        runtime = np.hstack(np.diff(runtime, axis=2)).T
        # runtime[:, :, 0] = -runtime[:, :, 0]
        # runtime = runtime.sum(axis=2)
        logger.debug(f"Runtime for {target} in {self.name} : {runtime}")
        return runtime.tolist()

    def mean_runtime(self, target: str) -> list[float]:
        if target in self.cache_runtime:
            logger.debug(
                f"Evaluation already calculated for {target} in {self.name}, using the cached value"
            )
            return self.cache_runtime[target]
        runtime = self.get_runtime(target)
        runtime = np.nanmean(runtime, axis=1)
        runtime[np.isnan(runtime)] = float("inf")
        logger.debug(f"Runtime for {target} in {self.name} : {runtime}")
        # we save the runtime in the cache
        self.cache_runtime[target] = runtime.tolist()
        return runtime.tolist()

    def mean_evaluation(self, target: str) -> list[float]:
        # if the evaluation has already been calculated we return it
        if target in self.cache_evaluation:
            logger.debug(
                f"Evaluation already calculated for {target} in {self.name}, using the cached value"
            )
            return self.cache_evaluation[target]

        evaluation = self.evaluation[target]
        if self.evaluation[target] is None:
            # the evaluation is a error message
            evaluation = [float("inf")] * len(self.arguments_label)
            self.cache_evaluation[target] = evaluation
            logger.debug(f"Evaluation for {target} in {self.name} : {evaluation}")
            return evaluation
        for i in range(len(evaluation)):
            for function in evaluation[i].keys():
                evaluation[i][function] = Task.str_and_none_to_nan(
                    evaluation[i][function]
                )
                if np.isnan(evaluation[i][function]).all():
                    evaluation[i][function] = float("inf")
                    continue
                evaluation[i][function] = np.nanmean(evaluation[i][function]).tolist()
                if np.isnan(evaluation[i][function]):
                    evaluation[i][function] = float("inf")
        logger.debug(f"Evaluation for {target} in {self.name} : {evaluation}")
        # we save the evaluation in the cache
        self.cache_evaluation[target] = evaluation
        return evaluation

    def standard_deviation(self, list_element) -> list[float]:
        return np.nanstd(list_element, axis=1).tolist()

    def variance(self, list_element) -> list[float]:
        return np.nanvar(list_element, axis=1).tolist()

    def get_status(self, target: str) -> str:
        """Getter for the status of the task.

        Returns
        -------
        status : str
            The status of the task.

        """
        mean = np.array(self.mean_runtime(target))
        if (mean == float("inf")).all():
            if isinstance(self.runtime[target][0], str):
                # the runtime is a error message
                return self.runtime[target][0]
            else:
                # we want to find the first error message

                return self.runtime[target][0][0][1]
        return "Run"


if __name__ == "__main__":
    from json_to_python_object import FileReaderJson

    FileReaderJson("results.json")

    print(Task.GetAllTaskName())
