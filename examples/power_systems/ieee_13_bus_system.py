from mygrid.grid import GridElements, ExternalGrid, Generation
from mygrid.grid import Shunt_Capacitor
from mygrid.grid import Substation, Sector, Switch, LineModel, UnderGroundLine
from mygrid.grid import Under_Ground_Conductor
from mygrid.grid import Section, LoadNode, TransformerModel, Conductor
from mygrid.grid import Auto_TransformerModel
from mygrid.util import R, P
from mygrid.util import p2r, r2p
import time
import numpy as np
ch1 = Switch(name='1', state=1)
ch2 = Switch(name='2', state=1)
spacing500=[0.0 + 28.0j,
            2.5 + 28.0j,
            7.0 + 28.0j,
            4.0 + 24.0j]

spacing505=[0.0 + 28.0j,
            7.0 + 28.0j,
            4.0 + 24.0j]

spacing510=[0.0 + 29.0j,
            0.5 + 24.0j]

spacing515=[0.0 + 0.0j,
            0.5 + 0.0j,
            1.0 + 0.0j]

spacing520=[0.0 + 0.0j,
            0.0833333 + 0.0j]

conduct1 = Conductor(id=75)
conduct2 = Conductor(id=44)
conduct3 = Conductor(id=31)

conduct4 = Under_Ground_Conductor(outsider_diameter=1.29,
                                  rp=0.4100,
                                  GMRp=0.0171,
                                  dp=0.567,
                                  k=13,
                                  rs=14.87,
                                  GMRs=0.00208,
                                  ds=0.0641,
                                  ampacity=None)

conduct5 = Under_Ground_Conductor(type="tapeshield",
                                  rp=0.97,
                                  GMRp=0.0111,
                                  dp=0.368,
                                  ds=0.88,
                                  T=5)
conduct6 = Conductor(id=32)


line601 =  LineModel(loc=spacing500,
                     phasing=['b','a','c','n'],
                     conductor=conduct1,
                     neutral_conductor=conduct2)

line602 =  LineModel(loc=spacing500,
                     phasing=['c','a','b','n'],
                     conductor=conduct2,
                     neutral_conductor=conduct2)

line603 =  LineModel(loc=spacing505,
                     phasing=['c','b','n'],
                     conductor=conduct3,
                     neutral_conductor=conduct3)

line604 =  LineModel(loc=spacing505,
                     phasing=['a','c','n'],
                     conductor=conduct3,
                     neutral_conductor=conduct3)

line605 =  LineModel(loc=spacing510,
                     phasing=['c','n'],
                     conductor=conduct3,
                     neutral_conductor=conduct3)

line606 =  UnderGroundLine(loc=spacing515,
                           phasing=['a','b','c'],
                           conductor=conduct4)

line607 =  UnderGroundLine(loc=spacing520,
                           phasing=['a', 'n'],
                           conductor=conduct5,
                           neutral_conductor=conduct6)

Zsys = np.array([[0.6273 + 6.0295j, -0.14 + 1.2443j, -0.14 + 1.2443j],
                 [-0.14 + 1.2443j, 0.6273 + 6.0295j, -0.14 + 1.2443j],
                 [-0.14 + 1.2443j,-0.14 + 1.2443j, 0.6273 + 6.0295j]], dtype = complex)




vll_ht = p2r(115e3, 0.0)
vll_mt = p2r(4.16e3, 0.0)
vll_bt = p2r(480.0, 0.0)
##############################capacitors########################################
capacitor_675 = Shunt_Capacitor(vll=4.16e3,
                                Qa=200e3, Qb=200e3, Qc=200e3,
                                type_connection="wye")

capacitor_611 = Shunt_Capacitor(vll=4.16e3,
                                Qa=0.0e3, Qb=0.0e3, Qc=100e3,
                                type_connection="wye")
##################################source########################################
eg1 = ExternalGrid(name='externgrid 1', vll=vll_ht)



node_sub_650 = LoadNode(name='650',
                        ppa=0.0e3 + 0.0e3j,
                        ppb=0.0e3 + 0.0e3j,
                        ppc=0.0e3 + 0.0e3j,
                        type_connection="wye",
                        zipmodel=[1.0, 0.0, 0.0],
                        external_grid=eg1,
                        voltage=vll_mt)
##################################Spot_Loads####################################
Load_Node632 = LoadNode(name='632',
                        ppa=0.0e3 + 0.0e3j,
                        ppb=0.0e3 + 0.0e3j,
                        ppc=0.0e3 + 0.0e3j,
                        type_connection="wye",
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_mt)
Load_Node634 = LoadNode(name='634',
                        ppa=160.0e3 + 110.0e3j,
                        ppb=120.0e3 + 90.0e3j,
                        ppc=120.0e3 + 90.0e3j,
                        type_connection="wye",
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_bt)
Load_Node645 = LoadNode(name='645',
                        ppa=0.0e3 + 0.0e3j,
                        ppb=170.0e3 + 125.0e3j,
                        ppc=0.0e3 + 0.0e3j,
                        type_connection="wye",
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_mt)
Load_Node646 = LoadNode(name='646',
                        ppa=0.0e3 + 0.0e3j,
                        ppb=230.0e3 + 132.0e3j,
                        ppc=0.0e3 + 0.0e3j,
                        type_connection="delta",
                        zipmodel=[0.0, 1.0, 0.0],
                        voltage=vll_mt)
Load_Node652 = LoadNode(name='652',
                        ppa=128.0e3 + 86.0e3j,
                        ppb=0.0e3 + 0.0e3j,
                        ppc=0.0e3 + 0.0e3j,
                        type_connection="wye",
                        zipmodel=[0.0, 1.0, 0.0],
                        voltage=vll_mt)
Load_Node671 = LoadNode(name='671',
                        ppa=385.0e3 + 220.0e3j,
                        ppb=385.0e3 + 220.0e3j,
                        ppc=385.0e3 + 220.0e3j,
                        type_connection="delta",
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_mt)
Load_Node675 = LoadNode(name='675',
                        ppa=485.0e3 + 190.0e3j,
                        ppb=68.0e3 + 60.0e3j,
                        ppc=290.0e3 + 212.0e3j,
                        type_connection="wye",
                        shunt_capacitor=capacitor_675,
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_mt)
Load_Node692 = LoadNode(name='692',
                        ppa=0.0e3 + 0.0e3j,
                        ppb=0.0e3 + 0.0e3j,
                        ppc=170.0e3 + 151.0e3j,
                        type_connection="delta",
                        zipmodel=[0.0, 0.0, 1.0],
                        voltage=vll_mt)
Load_Node611 = LoadNode(name='611',
                        ppa=0.0e3 + 0.0e3j,
                        ppb=0.0e3 + 0.0e3j,
                        ppc=170.0e3 + 80.0e3j,
                        type_connection="wye",
                        shunt_capacitor=capacitor_611,
                        zipmodel=[0.0, 0.0, 1.0],
                        voltage=vll_mt)

distributed_load = LoadNode(name='distload',
                        ppa=(17.0e3 + 10.0e3j),
                        ppb=(66.0e3 + 38.0e3j),
                        ppc=(117.0e3 + 68.0e3j),
                        type_connection="wye",
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_mt)

Load_Node633 = LoadNode(name='633',
                        voltage=vll_mt)

Load_Node684 = LoadNode(name='684',
                        voltage=vll_mt)
Load_Node680= LoadNode(name='680',
                        voltage=vll_mt)

#################################compesator#####################################
auto_650 = Auto_TransformerModel(name="auto_t1_650",
                                step=0.75,
                                tap_max=32,
                                vhold=122,
                                voltage=4.16e3,
                                R=3,
                                X=9,
                                CTP=700,
                                Npt=20,
                                Z=(1+1j)*1e-6)
################################transformers####################################
tf_Substation_t1 = TransformerModel(name="Substation_T1",
                      primary_voltage=vll_ht,
                      secondary_voltage=vll_mt,
                      power=5000e3,
                      connection='Dyn',
                      R=1,
                      X=8)

tf_XFM_1t1 = TransformerModel(name="XMF_1",
                      primary_voltage=vll_mt,
                      secondary_voltage=vll_bt,
                      connection='nyyn',
                      power=500e3,
                      R=1.1,
                      X=2)
#################################nodeconections#################################


node_regulator = LoadNode(name='regulator',
                             voltage=vll_mt)

#################################linesegments###################################

node_sub_650_to_node_regulator = Section(name='section2',
                                                 n1=node_sub_650,
                                                 n2=node_regulator,
                                                 #line_model=line601,
                                                 transformer=auto_650,
                                                 switch=ch1,
                                                 length=0)

node_regulator_to_Load_Node632 = Section(name='section3',
                                         n1=node_regulator,
                                         n2=Load_Node632,
                                         line_model=line601,
                                         length=2000/5280)

Load_Node632_to_Load_Node633 = Section(name='section4',
                                       n1=Load_Node632,
                                       n2=Load_Node633,
                                       line_model=line602,
                                       length=500/5280)

Load_Node632_to_Load_Node645 = Section(name='section5',
                                       n1=Load_Node632,
                                       n2=Load_Node645,
                                       line_model=line603,
                                       length=500/5280)

Load_Node632_to_distributed_load = Section(name='section6',
                                       n1=Load_Node632,
                                       n2=distributed_load,
                                       line_model=line601,
                                       length=0.5*2000/5280)

distributed_load_to_Load_Node671 = Section(name='section7',
                                       n1=distributed_load,
                                       n2=Load_Node671,
                                       line_model=line601,
                                       length=0.5*2000/5280)

Load_Node633_to_Load_Node634 = Section(name='section9',
                                       n1=Load_Node633,
                                       n2=Load_Node634,
                                       transformer=tf_XFM_1t1,
                                       length=0)

Load_Node645_to_Load_Node646 = Section(name='section10',
                                       n1=Load_Node645,
                                       n2=Load_Node646,
                                       line_model=line603,
                                       length=300/5280)

Load_Node671_to_Load_Node684 = Section(name='section11',
                                       n1=Load_Node671,
                                       n2=Load_Node684,
                                       line_model=line604,
                                       length=300/5280)

Load_Node671_to_Load_Node680 = Section(name='section12',
                                       n1=Load_Node671,
                                       n2=Load_Node680,
                                       line_model=line601,
                                       length=1000/5280)

Load_Node684_to_Load_Node652 = Section(name='section13',
                                       n1=Load_Node684,
                                       n2=Load_Node652,
                                       line_model=line607,
                                       length=800/5280)

Load_Node684_to_Load_Node611 = Section(name='section14',
                                       n1=Load_Node684,
                                       n2=Load_Node611,
                                       line_model=line605,
                                       length=300/5280)

Load_Node671_to_Load_Node692 = Section(name='section15',
                                       n1=Load_Node671,
                                       n2=Load_Node692,
                                       switch=ch2,
                                       line_model=line606,
                                       length=0.0/5280)

Load_Node692_to_Load_Node675 = Section(name='section16',
                                       n1=Load_Node692,
                                       n2=Load_Node675,
                                       line_model=line606,
                                       length=500/5280)

load_nodes = [node_sub_650, node_regulator, Load_Node632, Load_Node633,Load_Node680,
              Load_Node645, Load_Node671, Load_Node634, Load_Node646, Load_Node684, Load_Node652,
              Load_Node611, Load_Node692, Load_Node675, distributed_load]

sections = [node_sub_650_to_node_regulator,Load_Node671_to_Load_Node680,
            node_regulator_to_Load_Node632, Load_Node632_to_Load_Node633,
            Load_Node632_to_Load_Node645, Load_Node632_to_distributed_load,
            Load_Node633_to_Load_Node634, Load_Node645_to_Load_Node646,
            Load_Node671_to_Load_Node684, Load_Node684_to_Load_Node652,
            Load_Node684_to_Load_Node611, Load_Node671_to_Load_Node692,
            Load_Node692_to_Load_Node675, distributed_load_to_Load_Node671]
switchs = [ch1, ch2]

eg1.Z = tf_Substation_t1.A.dot(Zsys).dot(tf_Substation_t1.d) + tf_Substation_t1.z

grid_elements = GridElements(name='my_grid_elements')

grid_elements.add_switch(switchs)
grid_elements.add_load_node(load_nodes)
grid_elements.add_section(sections)
grid_elements.create_grid()

