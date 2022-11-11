# from logging import (
#     Logger,
#     getLogger
# )
from math import (
    floor,
    ceil
)

from .plate import Plate


class EchoPlate(Plate):

    def get_well_net_capacity(self, param_dead_volume: float) -> float:
        """Get the net capacity of the well.
        Multiple of 2.5 (ECHO)

        Parameters
        ----------
        param_dead_volume : float
            deadVolume of the parameter

        Returns
        -------
        float
            Well net capacity
        """
        return floor(
            (self.get_well_capacity()
             - self.get_dead_volume()
             - param_dead_volume) / 2.5
        ) * 2.5

    @staticmethod
    def get_raw_volume_per_well(
        volume: float,
        nb_wells: float
    ) -> float:
        """Get the raw volume per well.
        Multiple of 2.5 (ECHO)

        Parameters
        ----------
        volume : float
            Volume to fit to the well capacity
        nb_wells : float
            Number of wells to fit the volume to

        Returns
        -------
        float
            Raw volume per well
        """
        return ceil(
            volume / nb_wells / 2.5
        ) * 2.5

    @staticmethod
    def get_needed_nb_wells(
        volume: float,
        well_capacity: float
    ) -> int:
        """Get the number of wells in the plate.

        Parameters
        ----------
        volume : float
            Volume to fill the plate with
        well_capacity : float
            Well capacity

        Returns
        -------
        int
            Number of wells in the plate
        """
        return ceil(
            volume /
            well_capacity
        )
