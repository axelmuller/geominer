test_sets_1 = [{'hello world', '333', 42, 'no'},  {42, 51}, {'no hit'},
               {'house'}]         
test_sets_2 = [{42, 'bye world', 'yes'} , {'house'}, {11, 99}, {4, 9}]          
                                                                                
test_d1 = {'id' : range(len(test_sets_1)), 'ref' : test_sets_1}           
test_d2 = {'text' : test_sets_2}                                                
                                                                                
df_1 = pd.DataFrame(test_d1)                                                    
df_2 = pd.DataFrame(test_d2)  

df_1

df_2


desired_output = pd.DataFrame({'text' : test_sets_2, 'id' : ['0', '0', None,
                                                             '1']})
