from string import (
    ascii_uppercase as str_ascii_uppercase
)
from typing import (
    Dict,
    List,
    Tuple,
    Type
)
from logging import (
    Logger,
    getLogger
)
from json import (
    dumps as json_dumps,
    dump as json_dump,
    load as json_load
)
from re import split as re_split
from functools import reduce
from collections import Counter
from pandas import DataFrame

from .args import (
    DEFAULT_ARGS
)


class Plate:

    def __init__(
        self,
        nb_cols,
        nb_rows,
        dead_volume: int = DEFAULT_ARGS['SOURCE_PLATE_DEAD_VOLUME'],
        well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
        vertical: bool = True,
        logger: Logger = getLogger(__name__)
    ):
        """

        Parameters
        ----------
        nb_cols : int
            Number of plate columns
        nb_rows : int
            Number of plate rows
        dead_volume : int, optional
            Source plate deadVolume, by default 15000
        well_capacity : float, optional
            Capacity of each well, by default 60000
        logger : Logger, optional
            logger, by default getLogger(__name__)
        """
        self.__logger = logger
        self.__columns = [str(i+1) for i in range(nb_cols)]
        self.__rows = [
            f"{i}{j}" for i in ["", "A"] for j in str_ascii_uppercase
            ][:nb_rows]
        self.__vertical = vertical
        self.__cur_well_index = 0
        self.__dead_volume = dead_volume
        self.__well_capacity = well_capacity
        self.__wells = {}
        # self.__nb_empty_wells = self.get_nb_wells()
        self.__logger.debug(self)

    def __str__(self) -> str:
        return json_dumps(self.to_dict(), indent=4)

    def __eq__(self, other: Type['Plate']) -> bool:
        return (
            self.get_wells() == other.get_wells()
            and self.get_dead_volume() == other.get_dead_volume()
            and self.get_well_capacity() == other.get_well_capacity()
            and self.get_nb_rows() == other.get_nb_rows()
            and self.get_nb_columns() == other.get_nb_columns()
            # and self.get_nb_empty_wells() == other.get_nb_empty_wells()
        )

    def to_dict(self) -> str:
        return {
            'Dimensions': self.get_dimensions_str(),
            'deadVolume': self.get_dead_volume(),
            'Well capacity': self.get_well_capacity(),
            # 'Empty wells': self.get_nb_empty_wells(),
            'Current well': self.get_current_well(),
            'Parameters': self.get_list_of_parameters(),
            'Wells': self.get_wells()
        }

    def to_json(self, path: str) -> None:
        with open(path, 'w') as f:
            json_dump(self.to_dict(), f, indent=4)

    @staticmethod
    def from_json(
        path: str,
        logger: Logger = getLogger(__name__)
    ) -> 'Plate':
        with open(path, 'r') as f:
            d_plate = json_load(f)
        nb_rows, nb_cols = d_plate['Dimensions'].split('x')
        plate = Plate(
            nb_cols=int(nb_cols),
            nb_rows=int(nb_rows),
            dead_volume=d_plate['deadVolume'],
            well_capacity=d_plate['Well capacity']
        )
        plate.__wells = d_plate['Wells']
        # plate.__nb_empty_wells = d_plate['Empty wells']
        return plate

    def get_columns(self) -> List:
        return self.__columns

    def get_cols(self) -> List:
        return self.get_columns()

    def get_rows(self) -> List:
        return self.__rows

    def __get_row_by_index(self, index: int) -> str:
        """Get the row name of the well at the specified index.

        Parameters
        ----------
        index : int
            Well index

        Returns
        -------
        str
            Well row name
        """
        # if index >= self.get_nb_wells():
        #     msg = \
        #         f'The index {index} is greater than ' \
        #         f'the number of wells ({self.get_nb_wells()}).'
        #     raise(IndexError(msg))
        if self.__vertical:
            return self.get_rows()[index % self.get_nb_rows()]
        else:
            return self.get_rows()[index // self.get_nb_cols()]

    def __get_col_by_index(self, index: int) -> str:
        """Get the col name of the well at the specified index.

        Parameters
        ----------
        index : int
            Well index

        Returns
        -------
        str
            Well col name
        """
        # if index >= self.get_nb_wells():
        #     msg = \
        #         f'The index {index} is greater than ' \
        #         f'the number of wells ({self.get_nb_wells()}).'
        #     raise(IndexError(msg))
        if self.__vertical:
            return self.get_cols()[index // self.get_nb_rows()]
        else:
            return self.get_cols()[index % self.get_nb_cols()]

    def get_nb_rows(self) -> int:
        return len(self.__rows)

    def get_nb_cols(self) -> int:
        return self.get_nb_columns()

    def get_nb_columns(self) -> int:
        return len(self.__columns)

    def get_nb_wells(self) -> int:
        return self.get_nb_rows() * self.get_nb_columns()

    # def get_nb_empty_wells(self) -> int:
    #     return self.__nb_empty_wells

    def get_dimensions(self) -> Tuple:
        return self.get_nb_rows(), self.get_nb_columns()

    def get_dimensions_str(self) -> str:
        return f'{self.get_nb_rows()}x{self.get_nb_columns()}'

    def get_wells(self) -> Dict:
        return self.__wells

    def get_list_of_wells(self) -> Dict:
        return list(self.__wells.keys())

    def get_list_of_parameters(self) -> List:
        parameters = [list(well.keys()) for well in self.get_wells().values()]
        if parameters == []:
            return []
        return list(set(reduce(lambda x, y: x+y, parameters)))

    def get_well(self, well: str) -> Dict:
        return self.__wells.get(well, {})

    def __get_well_index(self, well: str) -> int:
        res = re_split(r'(\d+)', well)
        row = str(res[0])
        col = str(res[1])
        try:
            return \
                self.get_cols().index(col) * self.get_nb_rows() + \
                self.get_rows().index(row)
        except ValueError:
            msg = f'The well {well} is out of the current plate.'
            raise ValueError(msg)

    def get_well_volume(self, well: str) -> int:
        return sum(self.get_well(well).values())

    def get_dead_volume(self) -> int:
        return self.__dead_volume

    def get_well_capacity(self) -> float:
        return self.__well_capacity

    def __get_current_well_index(self) -> str:
        return self.__cur_well_index

    def get_current_well(
        self,
        logger: Logger = getLogger(__name__)
    ) -> str:
        """Get the current well."""
        return self.__get_well_name(
            self.__get_current_well_index(),
            logger
        )

    def well_out_of_range(self, well: str) -> bool:
        try:
            self.__get_well_index(well)
            return False
        except ValueError:
            return True

    def __get_well_name(
        self,
        well_index: int,
        logger: Logger = getLogger(__name__)
    ) -> str:
        """
        Convert well index into well coordinates

        Parameters
        ----------
        well_index : int
            Well index to return the name of
        logger: Logger
            Logger

        Returns
        -------
        well: str
            Well coordinates
        """
        return \
            f'{self.__get_row_by_index(well_index)}' \
            f'{self.__get_col_by_index(well_index)}'

    def next_well(self) -> str:
        """Change the current well to the next one.

        Returns
        -------
        str
            Name of the new current well
        """
        self.__set_current_well_by_index(self.__get_current_well_index() + 1)
        return self.get_current_well()

    def __set_current_well_by_index(self, index: int) -> None:
        """Set the current well from index.

        Parameters
        ----------
        index : int
            Index of the current well
        """
        if index >= self.get_nb_wells():
            msg = \
                f'The index {index} is greater than ' \
                f'the number of wells ({self.get_nb_wells()}).'
            # self.__logger.warning(msg)
            raise ValueError(msg)
        self.__cur_well_index = index
        # self.__logger.debug(
        #     f'The current well index is {self.__get_current_well_index()} '
        # )

    def set_current_well(self, well: str) -> None:
        """Set the current well from name.

        Parameters
        ----------
        well : str
            Name of the current well
        """
        self.__set_current_well_by_index(self.__get_well_index(well))
        self.__logger.debug(
            f'The current well name is {self.get_current_well()} '
        )

    # def set_nb_empty_wells(self, nb_empty_wells: int) -> None:
    #     """Set the number of empty wells.

    #     Parameters
    #     ----------
    #     nb_empty_wells : int
    #         Number of empty wells
    #     """
    #     self.__nb_empty_wells = min(nb_empty_wells, self.get_nb_wells())

    def fill_well(self, parameter: str, volume: float, well: str = '') -> None:
        """Fill the well with the given volume.

        Parameters
        ----------
        parameter : str
            Parameter to put in the well
        volume : float
            Volume to put in the well
        well : str, optional
            Name of the well to fill, by default use the current one
        """
        if well == '':
            well = self.get_current_well()
        if self.well_out_of_range(well):
            msg = f'The well {well} is out of the current plate.'
            raise IndexError(msg)
        # If well is empty,
        if well not in self.get_list_of_wells():
            # create it,
            self.__wells[well] = {}
            self.__wells[well][parameter] = 0
            # and the total volume is the added volume
            total_vol = volume
        elif parameter in self.get_well(well):  # The well already exists
            # The total volume is the sum of
            # the volume already in the well
            # and the added volume
            total_vol = self.get_well_volume(well) + volume
        else:
            self.__wells[well][parameter] = 0
            # The total volume is the added volume
            total_vol = volume
        # The total volume is greater than the well capacity
        if total_vol > self.get_well_capacity():
            msg = f'The volume {volume} is greater than ' \
                f'the well capacity {self.get_well_capacity()}.'
            raise ValueError(msg)
            # self.__logger.warning(
            #     f'The volume {volume} is greater than '
            #     f'the well capacity {self.get_well_capacity()}.'
            # )
        self.__logger.debug(
            f'Filling well {well} with {volume} of {parameter}'
        )
        self.__wells[well][parameter] += volume
        # self.set_nb_empty_wells(self.get_nb_empty_wells() - 1)

    def reindex_wells_by_factor(self, plate_id: str = '0') -> Dict:
        # Reindex plate by factors ID
        plate_by_factor = {}
        for well_id, well in self.get_wells().items():
            for factor in well.keys():
                if factor not in plate_by_factor:
                    plate_by_factor[factor] = {
                        'wells': list(),
                        'volumes': list()
                    }
                plate_by_factor[factor]['plt_id'] = plate_id
                plate_by_factor[factor]['wells'].append(well_id)
                plate_by_factor[factor]['volumes'].append(well[factor])
        return plate_by_factor

    @staticmethod
    def __get_volumes_per_factor(plates: List['Plate']) -> Dict:
        volume_by_factor = []
        # # Reindex plate by factors ID
        # for plt in plates:
        #     volume_by_factor.append(plt.reindex_wells_by_factor())
        # Sum volumes by factor
        for plt in plates:
            volume_by_factor.append(
                {
                    f: sum(p['volumes'])
                    for f, p in plt.reindex_wells_by_factor().items()
                }
            )
        # Sum volumes over all plates
        c = Counter()
        for vpf in volume_by_factor:
            c.update(vpf)
        return dict(c)

    @staticmethod
    def get_volumes_summary(
        plates: List['Plate'],
        type: str,
        logger: Logger = getLogger(__name__)
    ) -> Type:
        """Get a summary of the volumes per factor.

        Parameters
        ----------
        plates : List[Plate]
            List of plates

        Returns
        -------
        Type
            Summary of the volumes per factor
        """
        volumes = Plate.__get_volumes_per_factor(plates)
        if type == 'dict':
            return volumes
        elif type == 'pandas':
            vol_summary = DataFrame.from_dict(volumes, orient='index')
            vol_summary.index.name = 'Factor'
            vol_summary.columns = ['Sample+deadVolumes']
            return vol_summary
        else:  # 'str'
            return str(volumes)
