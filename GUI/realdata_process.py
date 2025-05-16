import netCDF4 as nc
import numpy as np
from obspy.taup import TauPyModel
from geopy.distance import geodesic
from math import cos
from scipy.interpolate import interp1d

class RealDataProcess():
    def __init__(self, latitude, longitude, NX, NY, XMIN, XMAX, YMIN, YMAX):
        self.vp_dataset = nc.Dataset('CRUST1.0-vp.r0.1.nc')
        self.vs_dataset = nc.Dataset('CRUST1.0-vs.r0.1.nc')
        self.rho_dataset = nc.Dataset('CRUST1.0-rho.r0.1.nc')

        self.latitude = latitude
        self.longitude = longitude
        if longitude < 0:
            self.longitude += 360
        self.NX = NX
        self.NY = NY
        self.XMIN = XMIN
        self.XMAX = XMAX
        self.YMIN = YMIN
        self.YMAX = YMAX

        self.latitudes = self.vp_dataset.variables['latitude'][:]
        self.longitudes = self.vp_dataset.variables['longitude'][:]
        self.lat_idx = np.abs(self.latitudes - latitude).argmin()
        self.lon_idx = np.abs(self.longitudes - longitude).argmin()

        # layers and average thickness
        self.layers = [
            ("water_vp", "water_vs", "water_rho", 3000),
            ("ice_vp", "ice_vs", "ice_rho", 2000),
            ("upper_sediments_vp", "upper_sediments_vs", "upper_sediments_rho", 2000),
            ("middle_sediments_vp", "middle_sediments_vs", "middle_sediments_rho", 3000),
            ("lower_sediments_vp", "lower_sediments_vs", "lower_sediments_rho", 5000),
            ("upper_crust_vp", "upper_crust_vs", "upper_crust_rho", 10000),
            ("middle_crust_vp", "middle_crust_vs", "middle_crust_rho", 15000),
            ("lower_crust_vp", "lower_crust_vs", "lower_crust_rho", 20000)
        ]
    
    def process(self):
        crust_depths = []
        crust_vp = []
        crust_vs = []
        crust_rho = []

        depth = 0  
        for vp_layer, vs_layer, rho_layer, thickness in self.layers:
            vp = self.vp_dataset.variables.get(vp_layer, None)
            vs = self.vs_dataset.variables.get(vs_layer, None)
            rho = self.rho_dataset.variables.get(rho_layer, None)

            # convert to m/s for vp and vs and to kg/m^3 for rho
            vp_val = float(vp[self.lat_idx, self.lon_idx]) * 1000 if vp is not None else np.nan
            vs_val = float(vs[self.lat_idx, self.lon_idx]) * 1000 if vs is not None else np.nan
            rho_val = float(rho[self.lat_idx, self.lon_idx]) * 1000 if rho is not None else np.nan

            crust_depths.append(depth)
            crust_vp.append(vp_val)
            crust_vs.append(vs_val)
            crust_rho.append(rho_val)

            depth += thickness

        crust_depths = np.array(crust_depths)
        crust_vp = np.array(crust_vp)
        crust_vs = np.array(crust_vs)
        crust_rho = np.array(crust_rho)

        # The IASP91 model
        model = TauPyModel("iasp91")
        iasp_depths = []
        iasp_vp = []
        iasp_vs = []
        iasp_rho = []  

        for layer in model.model.s_mod.v_mod.layers:
            d = layer[0] * 1000
            if d <= crust_depths[-1]:
                continue  # skip shallow layers

            iasp_depths.append(d)
            iasp_vp.append(layer[2] * 1000)
            iasp_vs.append(layer[3] * 1000)

            # Rough density estimate via Gardner's Equation
            rho_est = 0.31 * ((layer[2] * 1000) ** (0.25))  
            iasp_rho.append(rho_est * 1000)

        iasp_depths = np.array(iasp_depths)
        iasp_vp = np.array(iasp_vp)
        iasp_vs = np.array(iasp_vs)
        iasp_rho = np.array(iasp_rho)


        self.depth_combined = np.concatenate([crust_depths, iasp_depths])
        self.vp_combined = np.concatenate([crust_vp, iasp_vp])
        self.vs_combined = np.concatenate([crust_vs, iasp_vs])
        self.rho_combined = np.concatenate([crust_rho, iasp_rho])
    
    def calculate(self):
        DX = (self.XMAX - self.XMIN) / self.NX
        DY = (self.YMAX - self.YMIN) / self.NY

        # 1 degree latitude ≈ 111 km (constant)
        # 1 degree longitude ≈ 111 km × cos(latitude)
        epicenter = (self.latitude, self.longitude)
        deg_per_meter_lat = 1 / 111000 
        deg_per_meter_lon = 1 / (111000 * cos(self.latitude)) 
        origin_lat = epicenter[0] - (self.YMAX / 2) * deg_per_meter_lat
        origin_lon = epicenter[1]- (self.XMAX / 2) * deg_per_meter_lon

        y_meters = geodesic((origin_lat, origin_lon), (epicenter[0], origin_lon)).meters
        x_meters = geodesic((origin_lat, origin_lon), (origin_lat, epicenter[1])).meters

        # Convert to grid index
        self.source_x = min(max(int(x_meters / DX), 0), self.NX - 1)
        self.source_y = min(max(int(y_meters / DY), 0), self.NY - 1)

        depth_target = np.linspace(0, self.YMAX, self.NY)  # in meters

        vp_interp = interp1d(self.depth_combined, self.vp_combined, bounds_error=False, fill_value="extrapolate")
        vs_interp = interp1d(self.depth_combined, self.vs_combined, bounds_error=False, fill_value="extrapolate")
        rho_interp = interp1d(self.depth_combined, self.rho_combined, bounds_error=False, fill_value="extrapolate")

        vp_profile = vp_interp(depth_target)
        vs_profile = vs_interp(depth_target)
        rho_profile = rho_interp(depth_target)

        # Assign to full grid
        self.VEL_P = np.tile(vp_profile, (self.NX, 1))
        self.VEL_S = np.tile(vs_profile, (self.NX, 1))
        self.RHO = np.tile(rho_profile, (self.NX, 1))
