from datascience import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
plt.style.use("seaborn-muted")

def find_x_pos(widths):
    cumulative_widths = [0]
    cumulative_widths.extend(np.cumsum(widths))
    half_widths = [i/2 for i in widths]
    x_pos = []
    for i in range(0, len(half_widths)):
        x_pos.append(half_widths[i] + cumulative_widths[i])
    return x_pos

def plot_group(selection, ESG_sorted):
    selected_group = ESG_sorted.where("Group", selection)
    width, height = selected_group.column("Capacity_MW"), selected_group.column("Total_Var_Cost_USDperMWH")
    x_vals = find_x_pos(width)
    # Make the plot
    plt.figure(figsize=(9,6))
    plt.bar(x_vals, height, width=width, edgecolor = "black")
    # Add title and axis names
    plt.title(selection)
    plt.xlabel('Capacity_MW')
    plt.ylabel('Variable Cost')

    plt.show()
    
def price_calc(demand, sorted_table):
    price = 0
    sum_cap = 0
    for i in range(0,len(sorted_table['Capacity_MW'])):
        if sum_cap + sorted_table['Capacity_MW'][i] > demand:
            price = sorted_table['Total_Var_Cost_USDperMWH'][i]
            break
        else:
            sum_cap += sorted_table['Capacity_MW'][i]
            price = sorted_table['Total_Var_Cost_USDperMWH'][i]
    return price

def price_line_plot(price):
    plt.axhline(y=price, color='r', linewidth = 2)
    print("Price: " + str(price))
    
def demand_plot(demand):
    plt.axvline(x=demand, color='r', linewidth = 2)
    print("Capacity: " + str(demand))

    
def all_groups_with_demand(demand, ESG_sorted):
    width = ESG_sorted.column("Capacity_MW")
    height = ESG_sorted.column("Total_Var_Cost_USDperMWH")
    x_vals = find_x_pos(width)
    energy_colors_dict = {}
    count = 0
    colors = ['#EC5F67', '#F29056', '#F9C863', '#99C794', '#5FB3B3', '#6699CC', '#C594C5']
    for i in set(ESG_sorted['Group']):
        energy_colors_dict[i] = colors[count]
        count += 1
    colors_mapped = list(pd.Series(ESG_sorted['Group']).map(energy_colors_dict))
    ESG_sorted = ESG_sorted.with_column('Color', colors_mapped)
    group_colors = ESG_sorted.group("Group", lambda x: x).select("Group", "Color")
    group_colors["Color"] = group_colors.apply(lambda x: x[0], "Color")
    price = price_calc(demand, ESG_sorted)
    # Make the plot
    plt.figure(figsize=(9,6))
    plt.bar(x_vals, height, width=width, color=ESG_sorted['Color'], edgecolor = "black")
    patches = []
    for row in group_colors.rows:
        patches += [mpatches.Patch(color=row.item("Color"), label=row.item("Group"))]
    plt.legend(handles=patches, bbox_to_anchor=(1.1,1))
    plt.title('All Energy Sources')
    plt.xlabel('Capacity_MW')
    plt.ylabel('Variable Cost')
    price_line_plot(price)
    demand_plot(demand)
    
def profit(sorted_table, price):
    capacity_subset = sum(sorted_table.where("Total_Var_Cost_USDperMWH", are.below(price))["Capacity_MW"])
    revenue = capacity_subset * price
    cost = 0
    for i in range(len(sorted_table.where("Total_Var_Cost_USDperMWH", are.below(price))["Total_Var_Cost_USDperMWH"])):
        cost += sorted_table.where("Total_Var_Cost_USDperMWH", are.below(price))["Total_Var_Cost_USDperMWH"][i]\
        * sorted_table.where("Total_Var_Cost_USDperMWH", are.below(price))["Capacity_MW"][i]
    return revenue - cost

def calc_profit(selection, demand, ESG_sorted):
    price = price_calc(demand, ESG_sorted)
    selected_group = ESG_sorted.where("Group", selection)
    print("Your profit is ${:.2f}".format(profit(selected_group, price)))
    
def all_group_bids(demand, hour, sorted_joined_table):
    def price_calc(demand, sorted_table):
        price = 0
        sum_cap = 0
        for i in range(0,len(sorted_table['Capacity_MW'])):
            if sum_cap + sorted_table['Capacity_MW'][i] > demand:
                price = sorted_table['PRICE' + str(hour)][i]
                break
            else:
                sum_cap += sorted_table['Capacity_MW'][i]
                price = sorted_table['PRICE' + str(hour)][i]
        return price
    sorted_joined_table = sorted_joined_table.sort("PRICE" + str(hour))
    width = sorted_joined_table.column("Capacity_MW")
    height = sorted_joined_table.column('PRICE' + str(hour))
    x_vals = find_x_pos(width)
    energy_colors_dict = {}
    count = 0
    colors = ['#EC5F67', '#F29056', '#F9C863', '#99C794', '#5FB3B3', '#6699CC', '#C594C5']
    for i in set(sorted_joined_table['Group']):
        energy_colors_dict[i] = colors[count]
        count += 1
    colors_mapped = list(pd.Series(sorted_joined_table['Group']).map(energy_colors_dict))
    sorted_joined_table = sorted_joined_table.with_column('Color', colors_mapped)
    group_colors = sorted_joined_table.group("Group", lambda x: x).select("Group", "Color")
    group_colors["Color"] = group_colors.apply(lambda x: x[0], "Color")
    price = price_calc(demand, sorted_joined_table)
    # Make the plot
    plt.figure(figsize=(9,6))
    plt.bar(x_vals, height, width=width, color=sorted_joined_table['Color'], edgecolor = "black")
    patches = []
    for row in group_colors.rows:
        patches += [mpatches.Patch(color=row.item("Color"), label=row.item("Group"))]
    plt.legend(handles=patches, bbox_to_anchor=(1.1,1))
    plt.title('All Energy Sources')
    plt.xlabel('Capacity_MW')
    plt.ylabel('Price')
    price_line_plot(price)
    demand_plot(demand)
    
def your_portfolio_plot(selection, hour, demand, sorted_joined_table):
    def price_calc(demand, sorted_table):
        price = 0
        sum_cap = 0
        for i in range(0,len(sorted_table['Capacity_MW'])):
            if sum_cap + sorted_table['Capacity_MW'][i] > demand:
                price = sorted_table['PRICE' + str(hour)][i]
                break
            else:
                sum_cap += sorted_table['Capacity_MW'][i]
                price = sorted_table['PRICE' + str(hour)][i]
        return price
    your_source = sorted_joined_table.where("Group", selection)
    width_yours = your_source.column("Capacity_MW")
    height_yours = your_source.column('PRICE' + str(hour))
    height_yours_marginal_cost = your_source.column("Total_Var_Cost_USDperMWH")
    new_x_yours = find_x_pos(width_yours)
    energy_colors_dict = {}
    count = 0
    colors = ['#EC5F67', '#F29056', '#F9C863', '#99C794', '#5FB3B3', '#6699CC', '#C594C5']
    for i in set(sorted_joined_table['Group']):
        energy_colors_dict[i] = colors[count]
        count += 1
    colors_mapped = list(pd.Series(sorted_joined_table['Group']).map(energy_colors_dict))
    sorted_joined_table = sorted_joined_table.with_column('Color', colors_mapped)
    group_colors = sorted_joined_table.group("Group", lambda x: x).select("Group", "Color")
    group_colors["Color"] = group_colors.apply(lambda x: x[0], "Color")
    price = price_calc(demand, sorted_joined_table)
    # Make the plot
    plt.figure(figsize=(9,6))
    plt.bar(new_x_yours, height_yours, width=width_yours, 
            color = energy_colors_dict[selection], edgecolor = "black")
    plt.title(selection)
    plt.xlabel('Capacity_MW')
    plt.ylabel('Price')
    price_line_plot(price)

    plt.show()
    
def marginal_cost_plot(selection, hour, demand, sorted_joined_table):
    def price_calc(demand, sorted_table):
        price = 0
        sum_cap = 0
        for i in range(0,len(sorted_table['Capacity_MW'])):
            if sum_cap + sorted_table['Capacity_MW'][i] > demand:
                price = sorted_table['PRICE' + str(hour)][i]
                break
            else:
                sum_cap += sorted_table['Capacity_MW'][i]
                price = sorted_table['PRICE' + str(hour)][i]
        return price
    your_source = sorted_joined_table.where("Group", selection)
    width_yours = your_source.column("Capacity_MW")
    height_yours = your_source.column('PRICE' + str(hour))
    height_yours_marginal_cost = your_source.column("Total_Var_Cost_USDperMWH")
    new_x_yours = find_x_pos(width_yours)
    energy_colors_dict = {}
    count = 0
    colors = ['#EC5F67', '#F29056', '#F9C863', '#99C794', '#5FB3B3', '#6699CC', '#C594C5']
    for i in set(sorted_joined_table['Group']):
        energy_colors_dict[i] = colors[count]
        count += 1
    colors_mapped = list(pd.Series(sorted_joined_table['Group']).map(energy_colors_dict))
    sorted_joined_table = sorted_joined_table.with_column('Color', colors_mapped)
    group_colors = sorted_joined_table.group("Group", lambda x: x).select("Group", "Color")
    group_colors["Color"] = group_colors.apply(lambda x: x[0], "Color")
    price = price_calc(demand, sorted_joined_table)
    plt.figure(figsize=(9,6))
    num_x = len(your_source.where('PRICE' + str(hour), are.below(price))[1])
    plt.bar(new_x_yours[:num_x], height_yours_marginal_cost[:num_x], width=width_yours[:num_x], 
            color = energy_colors_dict[selection],
            edgecolor = "black")
    plt.title(selection)
    plt.xlabel('Capacity_MW')
    plt.ylabel('Marginal Cost')
    price_line_plot(price)

    plt.show()
    
def profit_by_hour(sorted_table, price, hour):
    capacity_subset = sum(sorted_table.where('PRICE' + str(hour), are.below(price))["Capacity_MW"])
    revenue = capacity_subset * price
    cost = 0
    for i in range(len(sorted_table.where('PRICE' + str(hour), are.below(price))["Total_Var_Cost_USDperMWH"])):
        cost += sorted_table.where('PRICE' + str(hour), are.below(price))["Total_Var_Cost_USDperMWH"][i]\
        * sorted_table.where('PRICE' + str(hour), are.below(price))["Capacity_MW"][i]
    return revenue - cost

def calc_profit_by_hour(selection, hour, demand, sorted_joined_table):
    def price_calc(demand, sorted_table):
        price = 0
        sum_cap = 0
        for i in range(0,len(sorted_table['Capacity_MW'])):
            if sum_cap + sorted_table['Capacity_MW'][i] > demand:
                price = sorted_table['PRICE' + str(hour)][i]
                break
            else:
                sum_cap += sorted_table['Capacity_MW'][i]
                price = sorted_table['PRICE' + str(hour)][i]
        return price
    price = price_calc(demand, sorted_joined_table)
    your_source = sorted_joined_table.where("Group", selection)
    print("Your profit is ${:.2f}".format(profit_by_hour(your_source, price, hour)))
    
    
    