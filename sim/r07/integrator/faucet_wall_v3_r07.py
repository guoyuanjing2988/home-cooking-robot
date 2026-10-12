"""GROHE13303000: full conservative wall-spout and plumbing envelopes.
OEM drawing: square60mm escutcheon,8mm depth,170mm outlet projection,
G1/2 male connection. The undimensioned body is covered by a full60x200x60mm
box, including its nose beyond the170mm outlet axis. No handle or swivel
exists on this different real product. No shape from33281003 is shrunk.
"""
import model
def install(root,c):
 w=root.find('worldbody');fc=c['replacement_faucet'];x,y,z=fc['wall_connection_m']
 def box(name,pos,size):model.box(w,'faucet_v3_'+name,pos,size,robot=False,color=(.65,.69,.72,1))
 box('wall_bracket_mating',[x,y-.004,z],[.060,.008,.060])
 box('fixed_spout_full_envelope',[x,y-.104,z],[.060,.192,.060])
 # Conservative complete100mm G1/2 stem/connector reservation behind the
 # explicitly authorized wall-mounted fixture. This is plumbing, not robot
 # structure. Wall dimensions and robot wall-contact policy stay unchanged.
 box('concealed_thread_and_connector',[x,y+.045,z],[.024,.110,.024])
 box('concealed_supply_pipe',[x,y+.045,(z+.20)/2],[.030,.030,z-.20])
 box('under_counter_supply',[x-.20,y-.01,.20],[.43,.14,.030])
 box('water_valve_service',[x-.40,y-.06,.155],[.150,.120,.110])
