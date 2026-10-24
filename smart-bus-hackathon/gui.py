from nicegui import ui
from core import ReservationSystem

rs = ReservationSystem()

ui.add_head_html('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Animated Dark Mesh Background */
    body { 
        background-color: #05050A;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        background-size: 200% 200%;
        animation: gradientShift 15s ease infinite;
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        transition: transform 0.3s ease, border-color 0.3s ease !important;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* Neon Text and Elements */
    .neon-text-cyan { color: #00f3ff; text-shadow: 0 0 10px rgba(0,243,255,0.5); }
    .neon-text-pink { color: #ff00ea; text-shadow: 0 0 10px rgba(255,0,234,0.5); }
    .neon-text-green { color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.5); }
    
    /* Sleek Inputs */
    .q-field__control {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: #fff !important;
    }
    .q-field__control:focus-within {
        border-color: #00f3ff !important;
        box-shadow: 0 0 15px rgba(0,243,255,0.2) !important;
    }

    /* Custom Header */
    .cyber-header {
        background: rgba(5, 5, 10, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* Tables */
    .q-table__container { background: transparent !important; }
    .q-table th { 
        background: rgba(0,0,0,0.4) !important; 
        color: #00f3ff !important; 
        font-weight: 800 !important;
        font-size: 13px !important;
        letter-spacing: 1px;
    }
    .q-table td { 
        color: #e2e8f0 !important; 
        font-size: 15px !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* Tabs */
    .q-tab { font-weight: 600 !important; color: #94a3b8 !important; }
    .q-tab--active { color: #00f3ff !important; text-shadow: 0 0 15px rgba(0,243,255,0.4); }
    .q-tab__indicator { background: #00f3ff !important; box-shadow: 0 0 10px #00f3ff; }
</style>
''')

# --- Refresh Functions ---
def refresh_all():
    update_metrics()
    update_chart()
    routes_table.rows = rs.routes
    routes_table.update()
    bookings_table.rows = rs.bookings
    bookings_table.update()
    update_report_text()

def update_metrics():
    rep = rs.report()
    lbl_revenue.text = f"Rs. {rep['revenue']}"
    lbl_seats.text = str(rep['seats_reserved'])
    lbl_bookings.text = str(rep['total_bookings'])
    lbl_fully.text = str(rep['fully_booked_routes'])

def update_chart():
    routes = rs.routes
    chart.options['xAxis']['data'] = [r['route_id'] for r in routes]
    chart.options['series'][0]['data'] = [r['total_seats'] - r['available_seats'] for r in routes]
    chart.update()

def update_report_text():
    rep = rs.report()
    text = f"""
    ### Financial Summary
    **Total Revenue:** Rs. {rep['revenue']}
    **Active Reservations:** {rep['confirmed_bookings']}
    **Cancelled Records:** {rep['cancelled_bookings']}
    
    ### Route Schedule by Departure City
    """
    for city, routes in rs.schedule().items():
        text += f"\n**📍 {city.upper()}**\n"
        if not routes:
            text += "   *No scheduled departures.*\n"
        else:
            for r in routes:
                text += f"   - {r['route_id']} → {r['destination']} ({r['departure_time']})\n"
    report_md.set_content(text)

# --- UI Layout ---
with ui.header().classes('cyber-header p-4 items-center justify-between'):
    with ui.row().classes('items-center gap-3'):
        ui.icon('rocket_launch', size='32px').classes('neon-text-cyan')
        ui.label('AERO TRANSIT').classes('text-3xl font-extrabold tracking-widest').classes('neon-text-cyan')
    ui.label('V 2.0 // HACKATHON EDITION').classes('text-xs text-slate-500 font-mono tracking-widest')

with ui.column().classes('w-full max-w-7xl mx-auto p-6 gap-6'):

    # --- TABS ---
    with ui.tabs().classes('w-full border-b border-white/10') as tabs:
        dash_tab = ui.tab('COMMAND CENTER', icon='insights')
        routes_tab = ui.tab('FLEET ROUTES', icon='route')
        book_tab = ui.tab('BOOK TICKET', icon='confirmation_number')
        bookings_tab = ui.tab('RESERVATIONS', icon='recent_actors')
        report_tab = ui.tab('DATA & ANALYTICS', icon='analytics')

    with ui.tab_panels(tabs, value=dash_tab).classes('w-full bg-transparent mt-4'):

        # ---------------- TAB 1: DASHBOARD ----------------
        with ui.tab_panel(dash_tab):
            with ui.row().classes('w-full gap-6'):
                # Metrics
                with ui.card().classes('glass-card w-[22%] p-6'):
                    ui.label('TOTAL REVENUE').classes('text-xs font-bold text-slate-400 tracking-widest')
                    lbl_revenue = ui.label('Rs. 0').classes('text-4xl font-extrabold neon-text-green mt-2')

                with ui.card().classes('glass-card w-[22%] p-6'):
                    ui.label('SEATS RESERVED').classes('text-xs font-bold text-slate-400 tracking-widest')
                    lbl_seats = ui.label('0').classes('text-4xl font-extrabold neon-text-cyan mt-2')

                with ui.card().classes('glass-card w-[22%] p-6'):
                    ui.label('TOTAL BOOKINGS').classes('text-xs font-bold text-slate-400 tracking-widest')
                    lbl_bookings = ui.label('0').classes('text-4xl font-extrabold neon-text-pink mt-2')

                with ui.card().classes('glass-card w-[22%] p-6'):
                    ui.label('FULLY BOOKED').classes('text-xs font-bold text-slate-400 tracking-widest')
                    lbl_fully = ui.label('0').classes('text-4xl font-extrabold text-red-400 mt-2')

            # Chart
            with ui.card().classes('glass-card w-full mt-6 p-8'):
                ui.label('LIVE OCCUPANCY METRICS').classes('text-sm font-bold text-slate-400 tracking-widest mb-4')
                chart = ui.echart({
                    'xAxis': {'type': 'category', 'data': [], 'axisLabel': {'color': '#94a3b8'}, 'axisLine': {'lineStyle': {'color': '#334155'}}},
                    'yAxis': {'type': 'value', 'axisLabel': {'color': '#94a3b8'}, 'splitLine': {'lineStyle': {'color': 'rgba(255,255,255,0.05)'}}},
                    'series': [{
                        'type': 'line',
                        'smooth': True,
                        'data': [],
                        'itemStyle': {'color': '#00f3ff'},
                        'lineStyle': {'width': 4, 'shadowColor': 'rgba(0,243,255,0.5)', 'shadowBlur': 10},
                        'areaStyle': {
                            'color': {
                                'type': 'linear', 'x': 0, 'y': 0, 'x2': 0, 'y2': 1,
                                'colorStops': [
                                    {'offset': 0, 'color': 'rgba(0,243,255,0.4)'},
                                    {'offset': 1, 'color': 'rgba(0,243,255,0.0)'}
                                ]
                            }
                        }
                    }],
                    'tooltip': {'trigger': 'axis'},
                    'grid': {'top': 30, 'bottom': 30, 'left': 40, 'right': 20}
                }).classes('w-full h-72')

        # ---------------- TAB 2: ROUTES ----------------
        with ui.tab_panel(routes_tab):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                ui.label('ACTIVE FLEET').classes('text-2xl font-extrabold text-white tracking-wide')
                search_input = ui.input(placeholder='Search destination or ID...').props('outlined dark dense clearable').classes('w-96')

            with ui.card().classes('glass-card w-full p-4'):
                routes_table = ui.table(
                    columns=[
                        {'name': 'route_id', 'label': 'ROUTE ID', 'field': 'route_id', 'align': 'left'},
                        {'name': 'departure', 'label': 'DEPARTURE', 'field': 'departure', 'align': 'left'},
                        {'name': 'destination', 'label': 'DESTINATION', 'field': 'destination', 'align': 'left'},
                        {'name': 'departure_time', 'label': 'TIME', 'field': 'departure_time', 'align': 'left'},
                        {'name': 'fare', 'label': 'FARE (RS.)', 'field': 'fare', 'align': 'left'},
                        {'name': 'available_seats', 'label': 'CAPACITY', 'field': 'available_seats', 'align': 'left'},
                    ],
                    rows=rs.routes, row_key='route_id'
                ).classes('w-full bg-transparent text-white')

                routes_table.add_slot('body-cell-available_seats', '''
                    <q-td :props="props">
                        <div class="flex items-center gap-2">
                            <q-linear-progress :value="props.value / props.row.total_seats" 
                                :color="props.value === 0 ? 'red' : (props.value < 15 ? 'amber' : 'cyan')" 
                                track-color="grey-9" size="8px" class="w-24 rounded-full" />
                            <span class="text-xs font-bold">{{ props.value }} / {{ props.row.total_seats }}</span>
                        </div>
                    </q-td>
                ''')

                def filter_routes(e):
                    val = e.value.lower() if e.value else ''
                    filtered = [r for r in rs.routes if val in r['route_id'].lower() or val in r['departure'].lower() or val in r['destination'].lower()]
                    routes_table.rows = filtered
                    routes_table.update()
                search_input.on('update:model-value', filter_routes)

        # ---------------- TAB 3: BOOK ----------------
        with ui.tab_panel(book_tab):
            with ui.row().classes('w-full justify-center mt-8'):
                with ui.card().classes('glass-card w-full max-w-2xl p-10'):
                    ui.label('SECURE YOUR SEAT').classes('text-2xl font-extrabold text-white tracking-wide mb-6 text-center neon-text-cyan')

                    with ui.row().classes('w-full gap-6'):
                        name_in = ui.input('Passenger Name').props('outlined dark').classes('w-full text-white')

                        with ui.row().classes('w-full gap-4'):
                            age_in = ui.input('Age').props('outlined dark').classes('w-1/2')
                            seats_in = ui.input('Number of Seats').props('outlined dark').classes('w-1/2')

                        # NEW: Generate the dropdown options dynamically from core.py
                        route_options = [f"{r['route_id']} - {r['departure']} to {r['destination']} (Rs. {r['fare']})" for r in rs.routes]
                        route_in = ui.select(options=route_options, label='Select Route').props('outlined dark use-input').classes('w-full')

                    def handle_booking():
                        try:
                            # Extract just the route ID (e.g. 'R101') from the dropdown text
                            selected_text = route_in.value
                            route_id = selected_text.split(" - ")[0] if selected_text else ""

                            b = rs.book(name_in.value, age_in.value, route_id, seats_in.value)
                            ui.notify(f'✅ Success! Booking ID: {b["booking_id"]}', type='positive', position='top-right', classes='bg-emerald-600 text-white')

                            # Clear the form
                            name_in.value = ''; age_in.value = ''; route_in.value = None; seats_in.value = ''
                            refresh_all()
                        except ValueError as e:
                            ui.notify(f'❌ {e}', type='negative', position='top-right', classes='bg-rose-600 text-white')

                    ui.button('CONFIRM RESERVATION', on_click=handle_booking).classes('w-full mt-6 py-4 text-lg font-bold rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-[0_0_20px_rgba(0,243,255,0.4)] transition-all')

        # ---------------- TAB 4: BOOKINGS ----------------
        with ui.tab_panel(bookings_tab):
            ui.label('MANAGE RESERVATIONS').classes('text-2xl font-extrabold text-white tracking-wide mb-4')

            with ui.card().classes('glass-card w-full p-4'):
                bookings_table = ui.table(
                    columns=[
                        {'name': 'booking_id', 'label': 'ID', 'field': 'booking_id', 'align': 'left'},
                        {'name': 'passenger_name', 'label': 'PASSENGER', 'field': 'passenger_name', 'align': 'left'},
                        {'name': 'route_id', 'label': 'ROUTE', 'field': 'route_id', 'align': 'left'},
                        {'name': 'seats', 'label': 'SEATS', 'field': 'seats', 'align': 'left'},
                        {'name': 'total_fare', 'label': 'TOTAL', 'field': 'total_fare', 'align': 'left'},
                        {'name': 'status', 'label': 'STATUS', 'field': 'status', 'align': 'left'},
                        {'name': 'actions', 'label': 'ACTIONS', 'align': 'center'}
                    ],
                    rows=rs.bookings, row_key='booking_id'
                ).classes('w-full bg-transparent text-white')

                bookings_table.add_slot('body-cell-status', '''
                    <q-td :props="props">
                        <q-badge :color="props.value === 'Confirmed' ? 'cyan' : 'grey'" class="text-xs font-bold px-3 py-1 rounded-full">
                            {{ props.value }}
                        </q-badge>
                    </q-td>
                ''')

                def cancel_selected(bid):
                    try:
                        rs.cancel(bid)
                        ui.notify(f'Booking cancelled.', type='warning', position='top-right', classes='bg-amber-600 text-white')
                        refresh_all()
                    except ValueError as e:
                        ui.notify(f'❌ {e}', type='negative', position='top-right', classes='bg-rose-600 text-white')

                bookings_table.add_slot('body-cell-actions', '''
                    <q-td :props="props">
                        <q-btn v-if="props.row.status === 'Confirmed'" color="rose" label="CANCEL" size="sm" flat class="font-bold" @click="() => $parent.$emit('cancel', props.row.booking_id)" />
                    </q-td>
                ''')
                bookings_table.on('cancel', lambda e: cancel_selected(e.args))

        # ---------------- TAB 5: ANALYTICS ----------------
        with ui.tab_panel(report_tab):
            with ui.card().classes('glass-card w-full p-10 mt-4'):
                ui.label('SYSTEM TELEMETRY').classes('text-2xl font-extrabold text-white tracking-wide mb-6')
                report_md = ui.markdown().classes('text-slate-300 text-lg leading-relaxed')

refresh_all()

ui.run(title="Aero Transit Premium", dark=True, port=8080, reload=False)