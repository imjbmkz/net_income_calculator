## Import package
import numpy as np
import streamlit as st

class NetIncome:
  '''
  Class to calculate government-mandated deductions, tax to be paid, 
  and take-home pay
  '''

  def __init__(self, basic_income, other_taxables=0, non_taxables=0):
    '''
    Instantiate the object with basic income (required), and optional 
    values for other_taxables and non-taxables
    '''
    self.basic_income = basic_income
    self.other_taxables = other_taxables
    self.non_taxables = non_taxables
  
  def pag_ibig(self):
    '''
    Calculate Pag-IBIG contribution
    '''
    if self.basic_income < 1_000:
      pag_ibig = 0

    elif self.basic_income >= 1_000 and self.basic_income <= 1_500:
      pag_ibig = self.basic_income * 0.01 # employee share

    else:
      pag_ibig = self.basic_income * 0.02 # employee share
    
    return 100 if pag_ibig > 100 else pag_ibig # limit to 100

  def philhealth(self):
    '''
    Calculate PhilHealth contribution
    '''
    return self.basic_income * 0.04 / 2 # 4% for 2022. ee-er share
  
  def sss(self, merge_mdf=True):
    '''
    Calculate SSS contribution including MDF
    '''

    ## Define employee compensation range
    compensation_min = np.arange(3_250, 25_000, 500)
    compensation_min = np.insert(compensation_min, 0, 0)

    ## Define employee regular contribution
    employee_contribution = np.arange(135, 922.5, 22.5)
    employee_contribution = np.insert(
        employee_contribution, 35, np.repeat(900, 10))
    
    ## Define employee mdf
    employee_mdf = np.arange(22.5, 247, 22.5)
    employee_mdf = np.insert(
        employee_mdf, 0, np.zeros(35)
    )
    
    ## Check if basic is not 0
    if self.basic_income == 0:
      return 0

    ## Initialize sss contribution, mdf
    sss_contribution = 0
    mdf = 0

    ## Get employee contribution
    for i in range(len(compensation_min)): 
      if self.basic_income < compensation_min[i]:
        sss_contribution = employee_contribution[i - 1]
        mdf = employee_mdf[i - 1]
        break
    
    sss_contribution = 900 if sss_contribution == 0 else sss_contribution
    mdf = 225 if mdf == 0 else mdf
    
    return sss_contribution + mdf if merge_mdf else (sss_contribution, mdf)

  def withholding_tax(self):
    '''
    Calculate monthly withholding tax
    '''

    ## Define total taxabble income
    total_deductions = sum([self.sss(), self.pag_ibig(), self.philhealth()])
    total_taxable_income = self.basic_income + self.other_taxables
    total_taxable_income -= total_deductions

    ## Define taxable compensation range
    compensation_min = [0, 20_834, 33_333, 66_667, 166_667, 666_667]

    ## Define base tax and tax rates
    base_tax = [0, 0, 2_500, 10_833.33, 40_833.33, 200_833.33]
    tax_rates = [0, 0.2, 0.25, 0.3, 0.32, 0.35]

    ## Define amount to deduct
    excess_of = [0, 20_834, 33_333, 66_667, 166_667, 666_667]

    ## Define withholding_tax
    tax = 0

    ## Get total tax
    for i in range(6):
      if total_taxable_income < compensation_min[i]:
        tax = base_tax[i - 1]
        tax += (total_taxable_income - 
                            excess_of[i - 1]) * tax_rates[i - 1]
        break
    
    ## Check if taxable salary is at level 6
    if total_taxable_income > 666_667:
      tax = base_tax[5]
      tax += (total_taxable_income - 666_667) * 0.35

    return tax
  
  def total_deductions(self):
    return sum([self.sss(True), self.pag_ibig(), 
                self.philhealth(), self.withholding_tax()])
    
  def total_earnings(self):
    return sum([self.basic_income, self.other_taxables, self.non_taxables])
  
  def take_home_pay(self):
    return self.total_earnings() - self.total_deductions()

## Streamlit app form
with st.form('net_income_form'):
    st.write('''
    ## Net Income Calculator
    ''')

    st.write('Fill out all fields of this form and click `calculate` button to get calculate your deductions and take-home pay.')
    basic_pay = st.number_input('Enter your basic pay:', value=750*21.5, format='%f')
    taxables = st.number_input('Enter total other taxables:', format='%f')
    non_taxables = st.number_input('Enter total non-taxables:', format='%f')
    
    ## Define take_home_pay variable to get deductions and net income
    take_home_pay = NetIncome(basic_pay, taxables, non_taxables)

    ## Submit button; calculate results
    submitted = st.form_submit_button("Calculate")
    if submitted:
        
        ## Print deductions
        st.write('Breakdown of salary deductions:')
        st.write('SSS: Php{:,.2f}'.format(take_home_pay.sss(False)[0]))
        st.write('SSS MDF: Php{:,.2f}'.format(take_home_pay.sss(False)[1]))
        st.write('PhilHealth: Php{:,.2f}'.format(take_home_pay.philhealth()))
        st.write('Pag-IBIG: Php{:,.2f}'.format(take_home_pay.pag_ibig()))
        st.write('Withholding Tax: Php{:,.2f}'.format(take_home_pay.withholding_tax()))
        st.write('')
        st.write('Take-home pay: Php{:,.2f}'.format(take_home_pay.take_home_pay()))