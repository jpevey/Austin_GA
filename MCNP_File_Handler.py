#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import collections
import sys


# In[2]:


class mcnp_file_handler:

    def __init__(self, template_file_string = "template_mcnp.inp", output_file_flag = "test_"):

        print("Let's play with some MCNP files!")
        self.data_dict = collections.OrderedDict()
        self.data_list = []
        
        ### build compile standard FNS materials
        self.setup_default_materials()
        
        ### building dictionary for material strings in this job
        self.mcnp_job_strings = collections.OrderedDict()
        
        self.template_file_string = template_file_string
        self.output_file_flag = output_file_flag
        
    def setup_default_materials(self):
        self.material_dict = collections.OrderedDict()
        self.material_dict['Water'] = collections.OrderedDict()
        self.material_dict['Water']['isotopes'] = [[0.11915,'1001'],
                                                      [0.88085,'8016']]
        
        self.material_dict['Water']            = [[[0.11915,'1001'],
                                                      [0.88085,'8016']],
                                                  1.0,
                                                  'wf']
        self.material_dict['Natural Uranium']  = [[[5.7*10**-5,'92234'],
                                                      [0.007204,  '92235'],
                                                      [0.992739,  '92238']],
                                                  18.8,
                                                  'wf']
        self.material_dict['Enriched Uranium'] = [[[2*10**-9,   '92232'],
                                                      [0.0026,     '92234'],
                                                      [0.0975,     '92235'],
                                                      [0.0046,     '92236'],
                                                      [0.895299998,'92238']],
                                                  18.94,
                                                  'wf']
        self.material_dict['Polyethylene']     = [[[0.143716,'1001'],
                                                      [0.856284,'6000']],
                                                  0.93,
                                                  'wf'] 
        self.material_dict['Flibe']            = [[[7.96355*10**-6,'3006'],
                                                      [0.18576341,    '3007'],
                                                      [0.059657085,   '4009'],
                                                      [0.754571541,   '9019']],
                                                  1.94362849,
                                                  'wf']
        self.material_dict['CaNaCl']           = [[[1.65875E-01,'11023'],
                                                      [4.67309E-01,'17035'],
                                                      [1.57972E-01,'17037'],
                                                      [2.01873E-01,'20040'],
                                                      [1.41463E-03,'20042'],
                                                      [3.02205E-04,'20043'],
                                                      [4.77797E-03,'20044'],
                                                      [9.57848E-06,'20046'],
                                                      [4.67271E-04,'20048']],
                                                  2.1596,
                                                  'wf']
        self.material_dict['MgNaCl']           =[[[1.55423E-01,'11023'],
                                                      [5.15798E-01,'17035'],
                                                      [1.74364E-01,'17037'],
                                                      [1.20383E-01,'12024'],
                                                      [1.58742E-02,'12025'],
                                                      [1.81582E-02,'12026']],
                                                  2.25775,
                                                  'wf']
    
    def set_job_materials(self, materials_list):
        self.job_materials = collections.OrderedDict()
        for mat_count, material in enumerate(materials_list):
            self.job_materials[mat_count + 1] = self.material_dict[material]
        print("Job materials: ", materials_list)
    
    def make_mcnp_material_strings(self):
        self.mcnp_job_strings['%materials%'] = "c Material Definitions"
        
        for material in self.job_materials:
            self.mcnp_job_strings['%materials%'] += "\nm"+str(material) + " "
            
            mat_mod_str = ' '
            if self.mcnp_job_strings['%materials%'][2] == 'wf':
                mat_mod_str = ' -'
            
            for mat in self.job_materials[material][0]:
                self.mcnp_job_strings['%materials%'] += str(mat[1]) + str(mat_mod_str) + str(mat[0]) + "\n      "
                
            ### removing unnec. spaces
            self.mcnp_job_strings['%materials%'] = self.mcnp_job_strings['%materials%'].strip()
        print(self.mcnp_job_strings['%materials%'])
        
        

    
    def combine_materials_wf(self, material_1, material_2, beta, new_material_string):
        #inputs should be of the form:[[[weightfraction,isotope text],[...],...],material_density]
        #for materials and a real number between 0 and 1 for beta which is 
        #the fraction of the new material that is material_1
        #an example material looks as follows:
        #water=[[[0.11915,'001001'],[0.88085,'008016']],1.0]
        
        # Setting materials
        material_1 = self.material_dict[material_1]
        material_2 = self.material_dict[material_2]
        
        if material_1[2] != 'wf' or material_2[2] != 'wf':
            print("Debug::::: materials:", material_1, material_2)
            print("A material is not in not in weight fraction format... exiting")
            sys.exit(1)
            
            
        #this will create the material_3 output so the next operations will work
        material_3=[[], 0, 'wf']
        #this will create the new density of the material
        material_3[1]=beta*material_1[1]+(1-beta)*material_2[1]
        material_3[1]=round(material_3[1],7)
        #
        #This insures that the fractional weights are normalized to 1
        sum_mat_1=0
        sum_mat_2=0
        for i in range(len(material_1[0])):
            sum_mat_1=sum_mat_1+material_1[0][i][0]
        for i in range(len(material_2[0])):
            sum_mat_2=sum_mat_2+material_2[0][i][0]
        if sum_mat_1!=1:
            for i in range(len(material_1[0])):
                material_1[0][i][0]=material_1[0][i][0]/sum_mat_1
        if sum_mat_2!=1:
            for i in range(len(material_2[0])):
                material_2[0][i][0]=material_2[0][i][0]/sum_mat_2
        #
        #initializing the new material 1 which will become material 3
        newmaterial_1=material_1
        newmaterial_2=material_2
        #
        #This creates the new material weight fractions based on the beta given
        for i in range(len(material_1[0])):
            newmaterial_1[0][i][0]=material_1[0][i][0]*beta
            newmaterial_1[0][i][0]=round(newmaterial_1[0][i][0],10)
        for i in range(len(material_2[0])):
            newmaterial_2[0][i][0]=material_2[0][i][0]*(1-beta)
            newmaterial_2[0][i][0]=round(newmaterial_2[0][i][0],10)
        #
        #adding editted materials input to create the new material
        material_3[0]=newmaterial_1[0]+newmaterial_2[0]
        #
        #This function outputs a new material "material_3" which has the same form as
        #the material inputs and the second output is a real number that is a combination of 
        #the two input densities
        self.material_dict[new_material_string] = material_3
        print("Created material:", new_material_string)
        return 
    
    #This is a function that will print an MCNP material card in the command window
    
    def MCNP_Material(self, material):
        #inputs should be of the form [[[weightfraction,isotope text],[...],...],material_density]
        #An example usage would be as follows were we use water as a material
        #water=[[[0.11915,'001001'],[0.88085,'008016']],1.0]
        #MCNP_Material(water)
        #
        #making the material name
        string='M1    '  
        #
        #This will insure that all the material fractons are unique. 
        fin=len(material[0])
        i=0
        test_uniq=fin-1
        while (i<test_uniq):
            j=i+1
            while (j<=test_uniq):
                if material[0][i][1]==material[0][j][1]:
                    material[0][i][0]=material[0][i][0]+material[0][j][0]
                    material[0].remove(material[0][j])
                    test_uniq=test_uniq-1
                j=j+1
            i=i+1
        #
        #This section prints the weightfractions and element in a form MCNP can read for all 
        #but the last because the need of spacing to line up for future observations
        for i in range(len(material[0])-1):
            string=string+str(material[0][i][1])
            string=string+'.70C -'
            string=string+str(material[0][i][0])
            string=string+'\n      '
        #
        #Prining the final part of the material weight fractions
        fin=len(material[0])
        string=string+str(material[0][fin-1][1])
        string=string+'.70C -'
        string=string+str(material[0][fin-1][0])
        #
        density=material[1]
        #
        #This function will not save a output. It just prints the MCNP material
        #We can edit this in the future to create a .txt file or something of like form
        return [string,density]

    #ranked from lowest atomic number to highest   
    #water=[[[0.11915,'001001'],[0.88085,'008016']],1.0]
    #natural_uranium=[[[5.7*10**-5,'092234'],[0.007204,'092235'],[0.992739,'092238']],18.8]
    #poly=[[[0.143716,'001001'],[0.856284,'006000']],0.93] 
    #enriched_fuel=[[[2*10**-9,'092232'],[0.0026,'092234'],[0.0975,'092235'],[0.0046,'092236'],[0.895299998,'092238']],18.94]
    #Flibe=[[[7.96355*10**-6,'003006'],[0.18576341,'003007'],[0.059657085,'004009'],[0.754571541,'009019']],1.94362849]
    #CaNaCl=[[[1.65875E-01,'011023'],[4.67309E-01,'017035'],[1.57972E-01,'017037'],[2.01873E-01,'020040'],[1.41463E-03,'020042'],[3.02205E-04,'020043'],[4.77797E-03,'020044'],[9.57848E-06,'020046'],[4.67271E-04,'020048']],2.1596]
    #MgNaCl=[[[1.55423E-01,'011023'],[5.15798E-01 ,'017035'],[1.74364E-01,'017037'],[1.20383E-01,'012024'],[1.58742E-02,'012025'],[1.81582E-02,'012026']],2.25775]
    
    #material_3=combine_materials_wf('Water','Natural Uranium',0.25)
#
    #material_4=combine_materials_wf(material_3,'Polyethylene',0.1)
#
    #print(MCNP_Material(material_4)[0])
    #print('Density:')
    #print(MCNP_Material(material_4)[1])
    def write_mcnp_input(self, job_number):
    
        run_file_list = []
        template_file = open(self.template_file_string , 'r')
        output_filename = self.output_file_flag +"_" + str(job_number) + ".inp"
        output_file = open(output_filename, 'w')
        
        target_dict = self.mcnp_job_strings
        
        for line in template_file:
            for target_string in target_dict:
                if target_string in line:
                    line = line.replace(str(target_string), str(target_dict[target_string]))
            output_file.write(line)
        output_file.close()
        template_file.close()
    
        return output_filename
        


# In[3]:


mcnp_f_h = mcnp_file_handler(template_file_string = "FluxRep_toy_template.inp", output_file_flag = "test_")

### combining materials
material_3=mcnp_f_h.combine_materials_wf('Water', 'Natural Uranium', 0.25, "material_3")
material_4=mcnp_f_h.combine_materials_wf("material_3", 'Polyethylene', 0.1, "material_4")

### adding materials to material list for this job
mcnp_f_h.set_job_materials(['Water', 'Flibe', 'material_4', 'material_3'])

### takes materials set in "set_job_materials" and makes the string needed by mcnp
mcnp_f_h.make_mcnp_material_strings()

mcnp_f_h.write_mcnp_input(job_number = '1')


# In[4]:




### combining materials
material_3=mcnp_f_h.combine_materials_wf('Water', 'Natural Uranium', 0.25, "material_3")
material_4=mcnp_f_h.combine_materials_wf("material_3", 'Polyethylene', 0.1, "material_4")

### adding materials to material list for this job
mcnp_f_h.set_job_materials(['Water', 'Flibe', 'material_4', 'material_3'])

### takes materials set in "set_job_materials" and makes the string needed by mcnp
mcnp_f_h.make_mcnp_material_strings()

mcnp_f_h.write_mcnp_input('1')



# In[5]:


my_dict = {'phone number':9843142 }


# In[6]:


my_dict['phone number']


# In[7]:


for mat in mcnp_f_h.job_materials:
    print(mcnp_f_h.job_materials[mat])


# In[ ]:




