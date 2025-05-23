from jaxtyping import Array, Float
from pancax.fem import Mesh, SimplexTriElement
from pancax.fem import create_higher_order_mesh_from_simplex_mesh
from pancax.fem import read_exodus_mesh
from pancax.timer import Timer
from typing import Optional, Union
import equinox as eqx
import jax.numpy as jnp


class BaseDomain(eqx.Module):
    mesh_file: str
    mesh: Mesh
    coords: Float[Array, "nn nd"]
    times: Union[Float[Array, "nt"], Float[Array, "nn 1"]]
    dt: float  # TODO assumes times were generated with linspace

    def __init__(
        self, mesh_file: str, times: Float[Array, "nt"],
        p_order: Optional[int] = 1
    ) -> None:
        with Timer("Reading Mesh..."):
            mesh = read_exodus_mesh(mesh_file)
            # if tri mesh, we can make it higher order from lower order
            if type(mesh.parentElement) is SimplexTriElement:
                mesh = create_higher_order_mesh_from_simplex_mesh(
                    mesh, p_order, copyNodeSets=True
                )
            else:
                print(
                    "WARNING: Ignoring polynomial \
                    order flag for non tri mesh"
                )

            if len(times) > 1:
                dt = times[1] - times[0]
            else:
                print(
                    "WARNING: setting dt = 0. since this is a \
                    static problem. Is this what you want?"
                )
                dt = 0.0

            self.mesh_file = mesh_file
            self.mesh = mesh
            self.coords = jnp.array(mesh.coords)
            self.times = times
            self.dt = dt
