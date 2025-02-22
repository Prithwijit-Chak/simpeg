import unittest

# from SimPEG import Mesh, PF
import discretize
from SimPEG.potential_fields import magnetics as mag
from SimPEG.utils.model_builder import getIndicesSphere
import numpy as np
from scipy.constants import mu_0


plotIt = False


class TestBoundaryConditionAnalytics(unittest.TestCase):
    def test_ana_boundary_computation(self):

        hxind = [(0, 25, 1.3), (21, 12.5), (0, 25, 1.3)]
        hyind = [(0, 25, 1.3), (21, 12.5), (0, 25, 1.3)]
        hzind = [(0, 25, 1.3), (20, 12.5), (0, 25, 1.3)]
        M3 = discretize.TensorMesh([hxind, hyind, hzind], "CCC")
        indxd, indxu, indyd, indyu, indzd, indzu = M3.face_boundary_indices
        mu0 = 4 * np.pi * 1e-7
        chibkg = 0.0
        chiblk = 0.01
        chi = np.ones(M3.nC) * chibkg
        sph_ind = getIndicesSphere([0, 0, 0], 100, M3.gridCC)
        chi[sph_ind] = chiblk
        mu = (1.0 + chi) * mu0
        Bbc, const = mag.analytics.CongruousMagBC(M3, np.array([1.0, 0.0, 0.0]), chi)

        flag = "secondary"
        Box = 1.0
        H0 = Box / mu_0
        Bbcxx, Bbcxy, Bbcxz = mag.analytics.MagSphereAnaFun(
            M3.gridFx[(indxd | indxu), 0],
            M3.gridFx[(indxd | indxu), 1],
            M3.gridFx[(indxd | indxu), 2],
            100,
            0.0,
            0.0,
            0.0,
            mu_0,
            mu_0 * (1 + chiblk),
            H0,
            flag,
        )
        Bbcyx, Bbcyy, Bbcyz = mag.analytics.MagSphereAnaFun(
            M3.gridFy[(indyd | indyu), 0],
            M3.gridFy[(indyd | indyu), 1],
            M3.gridFy[(indyd | indyu), 2],
            100,
            0.0,
            0.0,
            0.0,
            mu_0,
            mu_0 * (1 + chiblk),
            H0,
            flag,
        )
        Bbczx, Bbczy, Bbczz = mag.analytics.MagSphereAnaFun(
            M3.gridFz[(indzd | indzu), 0],
            M3.gridFz[(indzd | indzu), 1],
            M3.gridFz[(indzd | indzu), 2],
            100,
            0.0,
            0.0,
            0.0,
            mu_0,
            mu_0 * (1 + chiblk),
            H0,
            flag,
        )
        Bbc_ana = np.r_[Bbcxx, Bbcyy, Bbczz]

        if plotIt:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            ax.plot(Bbc_ana)
            ax.plot(Bbc)
            plt.show()
        err = np.linalg.norm(Bbc - Bbc_ana) / np.linalg.norm(Bbc_ana)

        assert err < 0.1, "Mag Boundary computation is wrong!!, err = {}".format(err)


if __name__ == "__main__":
    unittest.main()
