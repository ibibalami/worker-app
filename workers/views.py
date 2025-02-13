from django.shortcuts import render, redirect
from .models import Worker
from .forms import LocationForm, ExcelUploadForm
from django.http import HttpResponse
import math
import pandas as pd

def update_worker_type_from_excel(file_path):
    """Load the Excel file and update the worker types to 'agency' based on names found."""
    # Load the data from the specified Excel file into a DataFrame.
    df = pd.read_excel(file_path)

    # Loop through each name listed in the 'Name' column of the DataFrame.
    for name in df['Name']:
        try:
            # Attempt to retrieve a Worker object matching the current name.
            worker = Worker.objects.get(name=name)

            # If the worker is found, update their worker_type attribute to 'agency'.
            worker.worker_type = 'agency'
            worker.save()
            print(f"Successfully updated worker {worker.name} to agency.")
        except Worker.DoesNotExist:
            # If no worker is found, log a message indicating the absence of a match.
            print(f"No worker found with the name: {name}")

def upload_excel_view(request):
    """Handle the file upload for updating worker types from an Excel sheet."""
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            # Save the uploaded file temporarily for processing.
            with open('temp_file.xlsx', 'wb+') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)
            # Invoke the function to update worker types based on the Excel data.
            update_worker_type_from_excel('temp_file.xlsx')
            return HttpResponse("Worker types have been successfully updated based on the provided Excel file.")
    else:
        # If the request method is GET, instantiate a new form for uploading an Excel file.
        form = ExcelUploadForm()

    return render(request, 'upload_excel.html', {'form': form})

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth's surface."""
    R = 3958.8  # Radius of Earth in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * 
         math.cos(math.radians(lat2)) * 
         (math.sin(dlon / 2) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def location_finder(request):
    """Render the location finder page and calculate distances from the provided coordinates."""
    form = LocationForm(request.POST or None)
    query = request.GET.get('q', '')  # Get filter query from the template (if provided)
    
    if request.method == 'POST' and form.is_valid():
        lat = form.cleaned_data['latitude']
        long = form.cleaned_data['longitude']

        # Calculate distances to all predefined locations.
        distances = []
        for location in LOCATIONS:
            distance = haversine(lat, long, location['lat'], location['long'])
            distances.append((location, distance))

        # Optionally filter locations by name based on the query string.
        if query:
            distances = [(loc, dist) for loc, dist in distances if query.lower() in loc['name'].lower()]
        
        # Sort locations by distance and select the closest ones, limiting to 50%.
        distances = sorted(distances, key=lambda x: x[1])
        closest_locations = distances[:max(1, int(0.5 * len(distances)))]

        return render(request, 'workers/closest_locations.html', {'locations': closest_locations, 'query': query})
    
    return render(request, 'workers/location_form.html', {'form': form})

def worker_list(request):
    """Display a list of workers sorted by proximity to a given latitude and longitude."""
    if request.method == 'POST':
        lat = request.POST.get('lat')
        long = request.POST.get('long')

        # Convert latitude and longitude to float for calculations.
        lat = float(lat)
        long = float(long)

        # Calculate distances from the provided coordinates for all workers.
        workers = Worker.objects.all()
        distances = []
        for worker in workers:
            distance = haversine(lat, long, worker.lat, worker.long)
            distances.append((worker, distance))

        # Sort workers by distance and select the closest 50%.
        distances = sorted(distances, key=lambda x: x[1])
        closest_workers = distances[:max(1, int(0.5 * len(workers)))]

        return render(request, 'workers/worker_list.html', {'workers': closest_workers})

    else:
        # If the request method is GET, instantiate a new form for worker location input.
        form = LocationForm()

    return render(request, 'workers/worker_form.html', {'form': form})



# Predefined list of locations
LOCATIONS = [
   {'name': 'CYGNET KEWSTOKE', 'address': '123 Main St', 'lat': 51.365867, 'long': -2.964238},
    {'name': 'CYGNET HOSPITAL BURY', 'address': 'OFF BULLER ST, BOLTON RD, BURY UK', 'lat': 53.58624, 'long': -2.31713},
    {'name': 'CYGNET HOSPITAL COLCHESTER', 'address': 'BOXED RD, MILE END, COLCHESTER UK', 'lat': 51.92335, 'long': 0.89328},
    {'name': 'CYGNET HOSPITAL WYKE', 'address': 'BLANKNEY GRANGE, HUDDERSFIELD RD, BRADFORD', 'lat': 53.72844, 'long': -1.77432},
    {'name': 'CYGNET HOSPITAL MAIDSTONE', 'address': 'GIDDS POND WAY, WEAVERING, MAIDSTONE UK', 'lat': 51.28233, 'long': 0.55847},
    {'name': 'CYGNET HOSPITAL BRUNEL', 'address': 'Crow Ln, Henbury, Bristol', 'lat': 51.50948, 'long': -2.61768},
    {'name': 'CYGNET HOSPITAL DERBY', 'address': '100 London Rd, Derby, UK', 'lat': 52.9077, 'long': -1.45432},
    {'name': 'CYGNET HOSPITAL CLIFTON', 'address': 'Clifton Ln, Clifton, Nottingham, UK', 'lat': 52.90875, 'long': -1.18391},
    {'name': 'CYGNET HOSPITAL BLACKHEATH', 'address': '80-82 Blackheath Hill, Blackheath, London, UK', 'lat': 51.47243, 'long': -0.01068},
    {'name': 'CYGNET HOSPITAL HARROW', 'address': 'London Rd, Harrow, UK', 'lat': 51.56706, 'long': -0.33759},
    {'name': 'CYGNET ST. TEILO HOUSE', 'address': 'Goshen Cl, Rhymney, Tredegar, UK', 'lat': 51.76085, 'long': -3.28664},
    {'name': 'CYGNET LODGE KENTON', 'address': '74 Kenton Rd, Harrow, UK', 'lat': 51.58051, 'long': -0.31965},
    {'name': 'CYGNET HOSPITAL PADDOCKS', 'address': 'Wilmere Lane, Widnes', 'lat': 53.40012, 'long': -2.733833},
    {'name': 'CYGNET LEWISHAM LODGE', 'address': '123 Main St', 'lat': 51.452019, 'long': -0.012862},
    {'name': 'CYGNET HARROGATE', 'address': '23 Ripon Road, Harrogate ', 'lat': 53.999331, 'long': -1.547568},
    {'name': 'CYGNET OLDBURY', 'address': 'Salop Drive, Oldbury', 'lat': 52.478452, 'long': -1.994877},
    {'name': 'CYGNET BEECHES', 'address': 'Retford Road, South Leverton, Retford, Nottinghamshire', 'lat': 53.321247, 'long': -0.829178},
    {'name': 'CYGNET HOSPITAL WOLVERHAMPTON', 'address': '140 Wolverhampton Road, Wolverhampton, West Midlands', 'lat': 52.59799, 'long': -2.088916},
    {'name': 'CYGNET NIELD HOUSE', 'address': 'Bradfield Rd, Barrows Green, Crewe UK', 'lat': 53.11782, 'long': -2.46625},
    {'name': 'CYGNET HOSPITAL SHEFFIELD', 'address': '83 East Bank Road, Sheffield UK', 'lat': 53.36803, 'long': -1.45932},
    {'name': 'CYGNET WOKING', 'address': 'Redding Way, Knaphill, Woking, UK', 'lat': 51.31490, 'long': -0.61404},
    {'name': 'CYGNET NIGHTINGALE', 'address': '46-48 Stourcliffe Ave, Southbourne, Bournemouth, UK', 'lat': 50.72312, 'long': -1.81089},
    {'name': 'CYGNET MAPLE HOUSE', 'address': '93 Kneeton Rd, East Bridgford, Nottingham, UK', 'lat': 52.98543, 'long': -0.96553},
    {'name': 'CYGNET DELFRYN WARD', 'address': 'Argoed Hall Lane, Mold, UK', 'lat': 53.16799, 'long': -3.12503},
    {'name': 'CYGNET BROUGHTON WARD', 'address': 'High St, Brant Broughton, Lincoln UK', 'lat': 53.07380, 'long': -0.63444},
    {'name': 'CYGNET ST. WILLIAMS', 'address': 'Cornwall Ave, Darlington, UK', 'lat': 54.53461, 'long': -1.53647},
    {'name': 'CYGNET HOSPITAL STEVENAGE', 'address': 'Graveley Rd, Stevenage, UK', 'lat': 51.92794, 'long': -0.21409},
    {'name': 'CYGNET APPLETREE', 'address': 'Back, Frederick St N, Meadowfield, Durham, UK', 'lat': 54.75076, 'long': -1.62051},
    {'name': 'CYGNET PINDER HOUSE', 'address': 'Upper Sheffield Rd, Barnsley, UK', 'lat': 53.54267, 'long': -1.46764},
    {'name': 'CYGNET CEDARS', 'address': '37 Broadway Ave, Birmingham, UK', 'lat': 52.48166, 'long': -1.83555},
    {'name': 'CYGNET GLEDHOLT', 'address': '32 Greenhead Rd, Huddersfield, UK', 'lat': 53.64644, 'long': -1.79602},
    {'name': 'CYGNET THE ORCHARD', 'address': 'Station Rd, Thorrington, Colchester, UK', 'lat': 51.84367, 'long': 1.03102},
    {'name': 'CYGNET LODGE BRUGHHOUSE', 'address': '60 Rastrick Common, Rastrick, Brighouse, UK', 'lat': 53.69428, 'long': -1.78561},
    {'name': 'CYGNET ALARCH', 'address': 'Park Terrace, Merthyr Tydfil', 'lat': 51.321127, 'long': -2.964126},
    
    

    # ELYSIUM LOCATIONS
        {'name': 'ELYSIUM CHESTERFIELD HOUSE', 'address': '411 Newark Road, Lincoln', 'lat': 53.18366, 'long': -0.607688},
        {'name': 'ELYSIUM CLIPSTONE HOUSE', 'address': 'Clipstone House, First Avenue, Clipstone, Nottinghamshire', 'lat': 53.163458, 'long': -1.115965},
        {'name': 'ELYSIUM FIELD HOUSE', 'address': 'Chesterfield Rd, Shirland, Alfreton', 'lat': 53.098841, 'long': -1.390792},
        {'name': 'ELYSIUM HEALTHLINC APARTMENTS', 'address': 'Cliff Road, Welton, Lincolnshire', 'lat': 53.306084, 'long': -0.490114},
        {'name': 'ELYSIUM AVONFIELD NEUROLOGICAL CENTRE', 'address': 'Avonfield Neurological Centre, 290 Station Road, Knuston, Wellingborough', 'lat': 52.286237, 'long': -0.624439},
        {'name': 'ELYSIUM THE COTTAGE', 'address': '31 Norbeck Lane, Lincoln', 'lat': 53.304709, 'long': -0.487326},
        {'name': 'ELYSIUM THE FARNDON UNIT', 'address': 'Farndon Road, Newark, Nottinghamshire', 'lat': 53.066044, 'long': -0.83227},
        {'name': 'ELYSIUM THE LIMES', 'address': 'The Limes, Main Street, Langwith, Mansfield, Nottinghamshire', 'lat': 53.232217, 'long': -1.205352},
        {'name': 'ELYSIUM TOTTLE BROOK HOUSE', 'address': 'Tottle Brook House, Calverton Drive, Nottingham', 'lat': 52.978502, 'long': -1.225502},
        {'name': 'ELYSIUM ADDERLEY GREEN', 'address': 'Dividy Road, Stoke-On-Trent, Staffordshire', 'lat': 53.002705, 'long': -2.121448},
        {'name': 'ELYSIUM BADBY PARK', 'address': 'Badby Road West, Daventry, Northamptonshire', 'lat': 52.246658, 'long': -1.175337},
        {'name': 'ELYSIUM BALLINGTON HOUSE', 'address': 'Ballington Gardens, Leek, Staffordshire', 'lat': 53.103021, 'long': -2.021736},
        {'name': 'ELYSIUM BROOK HOUSE', 'address': 'Brook House, Station Road, Broadway, Worcestershire', 'lat': 52.040438, 'long': -1.869854},
        {'name': 'ELYSIUM COTSWOLD SPA HOSPITAL', 'address': 'Cotswold Spa, Station Road, Broadway, Worcestershire', 'lat': 52.040438, 'long': -1.869854},
        {'name': 'ELYSIUM STANLEY HOUSE & BOWLEY COURT', 'address': 'Bosbury, Hereford, Herefordshire', 'lat': 52.085718, 'long': -2.461053},
        {'name': 'ELYSIUM MOORLANDS NEUROLOGICAL CENTRE', 'address': 'Moorlands Neurological Centre, Lockwood Road, Cheadle, Staffordshire', 'lat': 53.000281, 'long': -1.962469},
        {'name': 'ELYSIUM THE WOODLANDS', 'address': '20 Woodland Avenue, Wolstanton, Newcastle Under Lyme', 'lat': 53.03272, 'long': -2.221382},
        {'name': 'ELYSIUM SPRING HOUSE', 'address': 'Spring House, Matford Road, Exeter', 'lat': 50.717664, 'long': -3.517024},
        {'name': 'ELYSIUM PINHOE VIEW', 'address': 'Pinhoe View, College Way, Exeter, Devon', 'lat': 50.731263, 'long': -3.469214},
        {'name': 'ELYSIUM THE AVALON CENTRE', 'address': 'The Avalon Centre, Edison Park, Hindle Way, Swindon, Wiltshire', 'lat': 51.557195, 'long': -1.731115},
        {'name': 'ELYSIUM THE COPSE', 'address': 'The Copse, Beechmount Close, Oldmixon, Weston-super-Mare, Somerset', 'lat': 51.321127, 'long': -2.964126},
        {'name': 'ELYSIUM THE DEAN NEUROLOGICAL CENTRE', 'address': 'The Dean Neurological Centre, Tewkesbury Road, Gloucester', 'lat': 51.880048, 'long': -2.239392},
        {'name': 'ELYSIUM THE WOODMILL', 'address': 'The Woodmill, Exeter Road, Cullompton, Devon', 'lat': 50.847373, 'long': -3.394716},
        {'name': 'ELYSIUM WELLESLEY', 'address': 'Westpark 26, Chelston, Wellington, Somerset', 'lat': 50.978961, 'long': -3.205618},
        {'name': 'ELYSIUM ABERBEEG', 'address': 'Aberbeeg Hospital, Pendarren Road, Aberbeeg, Abertillery', 'lat': 51.707378, 'long': -3.14975},
        {'name': 'ELYSIUM ADERYN', 'address': 'Penperlleni, Nr Pontypool, Monmouthshire, Wales', 'lat': 51.735642, 'long': -2.982887},
        {'name': 'ELYSIUM CEFN CARNAU', 'address': 'Cefn Carnau Lane, Thornhill, Cardiff, South Wales', 'lat': 51.556889, 'long': -3.210069},
        {'name': 'ELYSIUM REENE HOUSE', 'address': 'Reene House, Reene Court, Lliswerry, Newport, Wales', 'lat': 51.580688, 'long': -2.961615},
        {'name': 'ELYSIUM TY GLYN EBWY', 'address': 'Tŷ Glyn Ebwy, Hillside, Ebbw Vale, Blaenau, Gwent', 'lat': 51.77465, 'long': -3.209118},
        {'name': 'ELYSIUM TY GROSVENOR', 'address': '16 Grosvenor Road, Wrexham, Wales', 'lat': 53.048576, 'long': -2.996915},
        {'name': 'ELYSIUM TY GWYN HALL', 'address': 'Llantilio Pertholey, Abergavenny, Monmouthshire, Wales', 'lat': 51.841987, 'long': -3.004711},
        {'name': 'ELYSIUM TYDFIL HOUSE', 'address': 'Tydfil House, 46 Merthyr Rd, Abergavenny', 'lat': 51.823226, 'long': -3.025115},
    

        #NEUVEN LOCATIONS

        {'name': 'NEUVEN BIRNBECK HOUSE', 'address': '2 St Paul\'s Road, Weston-super-Mare', 'lat': 51.337154, 'long': -2.974144},
        {'name': 'NEUVEN APPLEY CLIFF', 'address': 'Appley Cliff, Popham Road, Shanklin', 'lat': 50.624841, 'long': -1.175553},
        {'name': 'NEUVEN ST CECILIA\'S', 'address': '32 Sundridge Avenue, Bromley', 'lat': 51.410013, 'long': 0.039039},
        {'name': 'NEUVEN LEONARD CHESHIRE - NEWHAVEN ROAD', 'address': '161-163 Newhaven Road, Edinburgh', 'lat': 55.976039, 'long': -3.193087},
        {'name': 'NEUVEN LEONARD CHESHIRE - ALEMOOR', 'address': '17 Alemoor Crescent, Edinburgh', 'lat': 55.964615, 'long': -3.156706},
        {'name': 'NEUVEN LEONARD CHESHIRE - WARDIEBURN', 'address': '4 Wardieburn Street East, Edinburgh', 'lat': 55.977576, 'long': -3.225057},
        {'name': 'NEUVEN WHARFEDALE HOUSE', 'address': '16 Wharfedale Lawns, Wetherby', 'lat': 53.929179, 'long': -1.388136},
        {'name': 'NEUVEN MID SHIRES SUPPORTED LIVING SERVICE', 'address': 'Room 9 & 10 Dombey Court, The Pilgrim Centre, Brickhill Drive, Bedford', 'lat': 52.150112, 'long': -0.458966},
        {'name': 'NEUVEN ILEX CLOSE', 'address': 'Ilex Close, Rustington, Littlehampton', 'lat': 50.805843, 'long': -0.503728},
        {'name': 'NEUVEN RADFORD CLOSE', 'address': 'Radford Close, Offerton, Stockport', 'lat': 53.395885, 'long': -2.115812},
        {'name': 'NEUVEN MOTE LODGE', 'address': 'Mote Lodge, High Street, Staplehurst, Tonbridge', 'lat': 51.180728, 'long': 0.52155},
        {'name': 'NEUVEN EFFINGHAM LANE', 'address': 'Effingham Lane, Copthorne, Crawley', 'lat': 51.11424, 'long': -0.092138},
        {'name': 'NEUVEN NEWCASTLE ROAD', 'address': 'Newcastle Road, Sandbach', 'lat': 53.148105, 'long': -2.366149},
        {'name': 'NEUVEN WOOLTON ROAD', 'address': 'Woolton Road, Liverpool', 'lat': 53.372334, 'long': -2.855824},
        {'name': 'NEUVEN STADON ROAD', 'address': '42 Stadon Road, Anstey, Leicester', 'lat': 52.657248, 'long': -1.201121},
        {'name': 'NEUVEN ST ANDREWS WAY', 'address': '3 St Andrews Way, Deans, Livingston', 'lat': 55.887186, 'long': -3.511367},
        {'name': 'NEUVEN LLANHENNOCK', 'address': 'Llanhennock, Caerleon, Newport', 'lat': 51.616313, 'long': -2.93319},
        {'name': 'NEUVEN GREENACRES', 'address': 'Greenacres Bow Arrow Lane, Dartford', 'lat': 51.446648, 'long': 0.223953},
        {'name': 'NEUVEN PORTOBELLO', 'address': 'Portobello, Edinburgh', 'lat': 55.95058, 'long': -3.11491},
        {'name': 'NEUVEN LUCAS LANE', 'address': 'Lucas Lane, Hitchin', 'lat': 51.94786, 'long': -0.278153},
        {'name': 'NEUVEN KNOCKBREDA ROAD', 'address': '126 Upper Knockbreda Road, Belfast', 'lat': 54.563023, 'long': -5.868088},
        {'name': 'NEUVEN NESS WALK', 'address': 'Ness Walk, Inverness', 'lat': 57.477682, 'long': -4.224999},
        {'name': 'NEUVEN CLOCK BARN LANE', 'address': 'Clock Barn Lane, Godalming', 'lat': 51.183312, 'long': -0.616975},
        {'name': 'NEUVEN LONG ROCK', 'address': 'Long Rock, Penzance', 'lat': 50.117542, 'long': -5.537028},
        {'name': 'NEUVEN LAVENDER FIELDS', 'address': '2 Lavender Fields, Lucas Lane, Hitchin', 'lat': 51.94786, 'long': -0.278153},
        {'name': 'NEUVEN ARGYLE STREET', 'address': '7/9 Argyle Street, Edinburgh', 'lat': 55.97644, 'long': -3.200136},
        {'name': 'NEUVEN KIRKLANDS PARK RIGG', 'address': '2 Kirklands Park Rigg, Kirkliston', 'lat': 55.95869, 'long': -3.410451},
        {'name': 'NEUVEN FREELANDS ROAD', 'address': '69 Freelands Road, Bromley', 'lat': 51.401246, 'long': 0.046893},
        {'name': 'NEUVEN WARWICK ROAD', 'address': 'Warwick Road, Banbury', 'lat': 52.051627, 'long': -1.335558},
        {'name': 'NEUVEN BLAIR AVENUE', 'address': 'Blair Avenue, Glenrothes', 'lat': 56.20367, 'long': -3.189162},
        {'name': 'NEUVEN FARNCOMBE ROAD', 'address': '9 Farncombe Road, Worthing', 'lat': 50.8144, 'long': -0.378201},
        {'name': 'NEUVEN FOURACRES', 'address': 'Fouracres, Woodgates Lane, North Ferriby', 'lat': 53.71691, 'long': -0.501929},
        {'name': 'NEUVEN PEMBURY ROAD', 'address': 'Pembury Road, Tunbridge Wells', 'lat': 51.167321, 'long': 0.268894},
        {'name': 'NEUVEN CHURCH ROAD', 'address': 'Church Road, Brampton, Huntingdon', 'lat': 52.31599, 'long': -0.168132},
        {'name': 'NEUVEN QUANTOK ROAD', 'address': '15 Quantock Road, Weston-super-Mare', 'lat': 51.340339, 'long': -2.975939},
        {'name': 'NEUVEN CHARLTON LANE', 'address': 'Charlton Lane, Leckhampton, Cheltenham', 'lat': 51.867308, 'long': -2.077267},
        {'name': 'NEUVEN COLLEGE ROAD', 'address': '138 College Road, London', 'lat': 51.473186, 'long': -0.181634},
        {'name': 'NEUVEN WORTHINGTON CLOSE', 'address': 'Worthington Close, Crook', 'lat': 54.634507, 'long': -1.564149},
        {'name': 'NEUVEN BANSTEAD ROAD', 'address': '17 Banstead Road, Ewell, Epsom', 'lat': 51.352506, 'long': -0.265175},
        {'name': 'NEUVEN HALL ROAD', 'address': 'Hall Road, Great Bromley, Colchester', 'lat': 51.938071, 'long': 0.944124},
        {'name': 'NEUVEN BRADBURY WING', 'address': 'The Bradbury Wing, Roseberry Crescent, Jesmond, Newcastle upon Tyne', 'lat': 54.992189, 'long': -1.582091},
        {'name': 'NEUVEN VESEY ROAD', 'address': '39 Vesey Road, Sutton Coldfield', 'lat': 52.586503, 'long': -1.826905},
        {'name': 'NEUVEN ALMA ROAD', 'address': '42 Alma Road, Reigate', 'lat': 51.240191, 'long': -0.203195},
        {'name': 'NEUVEN MAPLE ROAD', 'address': '10 Maple Road, Penge, London', 'lat': 51.403594, 'long': -0.051743},
        {'name': 'NEUVEN KING STREET', 'address': '61/63 King Street, Sileby, Loughborough', 'lat': 52.724268, 'long': -1.103354},
        {'name': 'NEUVEN LODGE ROAD', 'address': 'Lodge Road, Kingswood, Bristol', 'lat': 51.42512, 'long': -2.478376},
        {'name': 'NEUVEN MAIN STREET', 'address': 'Main Street, Netherseal, Swadlincote', 'lat': 52.678413, 'long': -1.540186},
        {'name': 'NEUVEN BLACKADDER PLACE', 'address': '1/7 Blackadder Place, Edinburgh', 'lat': 55.956582, 'long': -3.18775},
        {'name': 'NEUVEN FRYERS CLOSE', 'address': 'Fryers Close, Botley Road, Romsey', 'lat': 50.991882, 'long': -1.497607},
        {'name': 'NEUVEN PEMBURY ROAD', 'address': 'Pembury Road Tunbridge Wells post town, Kent', 'lat': 51.167321, 'long': 0.268894},
        {'name': 'NEUVEN RADFORD CLOSE', 'address': 'Radford Close Offerton, Stockport, Greater Manchester', 'lat': 53.395885, 'long': -2.115812},
        {'name': 'NEUVEN LODGE ROAD', 'address': 'Lodge Road, Bristol, South Gloucestershire', 'lat': 51.45343, 'long': -2.562419},
        {'name': 'NEUVEN SOROGOLD CLOSE', 'address': '22 Sorogold Close, Merseyside', 'lat': 53.475847, 'long': -2.892222},
        {'name': 'NEUVEN ST JOHNS ROAD', 'address': '17 St Johns Rd, Arlesey', 'lat': 52.029973, 'long': -0.293576},
        {'name': 'NEUVEN ALMA ROAD', 'address': '42 Alma Rd Reigate Surrey', 'lat': 51.240191, 'long': -0.203195},
        {'name': 'NEUVEN CANDLEFORD ROAD', 'address': '1a Candleford Road, Off Palatine Road, Didsbury', 'lat': 53.441145, 'long': -2.22735},
        {'name': 'NEUVEN GIBFIELD ROAD', 'address': 'Gibfield Road, Colne, Lancashire', 'lat': 53.857905, 'long': -2.179775},
        {'name': 'NEUVEN MARINE PARADE', 'address': 'Marine Parade, Dovercourt, Harwich, Essex', 'lat': 51.938266, 'long': 1.27416},
        {'name': 'NEUVEN MURFORD AVENUE', 'address': '15 Murford Avenue, Bristol', 'lat': 51.467896, 'long': -2.609863},
        {'name': 'NEUVEN WORKINGTON', 'address': 'Workington, Cumbria', 'lat': 54.646388, 'long': -3.558343},
        {'name': 'NEUVEN GILBERT SCOTT ROAD', 'address': 'Gilbert Scott Rd, South Horrington Village, Wells', 'lat': 51.210046, 'long': -2.642765},
        {'name': 'NEUVEN ANSDELL ROAD', 'address': '18 Ansdell Rd S, Lytham Saint Annes', 'lat': 53.737832, 'long': -2.976831},
        {'name': 'NEUVEN BURTON ROAD', 'address': 'Burton Rd, Acresford, Swadlincote', 'lat': 52.723911, 'long': -1.546057},
        {'name': 'NEUVEN PARBOLD', 'address': 'Parbold, Wigan', 'lat': 53.601179, 'long': -2.79924},
        {'name': 'NEUVEN BLUEBELL CLOSE', 'address': '140 Bluebell Close, Beacon Lough, Gateshead', 'lat': 54.955951, 'long': -1.589972},
        {'name': 'NEUVEN LONG CAUSEWAY', 'address': 'Long Causeway, Exmouth, Devon', 'lat': 50.62201, 'long': -3.394106},
        {'name': 'NEUVEN ORCHARD LANE', 'address': 'Orchard Lane, null, Crewkerne, Somerset', 'lat': 50.867189, 'long': -2.78865},
        #NEUVEN LOCATIONS

        {'name': 'NHS CHERRY WARD', 'address': 'BOWMERE HOSPITAL, LIVERPOOL ROAD, CHESTER', 'lat': 53.211544, 'long': -2.898825},
        {'name': 'NHS JUNIPER WARD', 'address': 'BOWMERE HOSPITAL, LIVERPOOL ROAD, CHESTER', 'lat': 53.211544, 'long': -2.898825},
        {'name': 'NHS BEECH WARD', 'address': 'BOWMERE HOSPITAL, LIVERPOOL ROAD, CHESTER', 'lat': 53.211544, 'long': -2.898825},
        {'name': 'NHS WILLOW WARD', 'address': 'BOWMERE HOSPITAL, LIVERPOOL ROAD, CHESTER', 'lat': 53.211544, 'long': -2.898825},
        {'name': 'NHS CORAL WARD', 'address': 'BOWMERE HOSPITAL, LIVERPOOL ROAD, CHESTER', 'lat': 53.211544, 'long': -2.898825},
        {'name': 'NHS GREENWAYS', 'address': 'Rosemount, Lea Bank Close, Chester Road, Greenways, Macclesfield', 'lat': 53.260823, 'long': -2.146286},
        {'name': 'NHS INDIGO WARD', 'address': 'ANCORA HOUSE, LIVERPOOL RD., CHESTER', 'lat': 53.211544, 'long': -2.898825},
        {'name': 'NHS MEADOWBANK WARD', 'address': 'SPRINGVIEW, CLATTERBRIDGE RD., BEBINGTON', 'lat': 53.332283, 'long': -3.025848},
        {'name': 'NHS OLD HALL SURGERY', 'address': 'Old Hall Surgery, 26 Stanney Lane, Ellesmere Port, Cheshire', 'lat': 53.276214, 'long': -2.904396},
        {'name': 'NHS RIVERWOOD', 'address': 'SPRINGVIEW, CLATTERBRIDGE RD., BEBINGTON', 'lat': 53.332283, 'long': -3.025848},
        {'name': 'NHS SILK WARD', 'address': 'Silk Ward Macclesfield District Hospital, Victoria Road, Macclesfield, Cheshire', 'lat': 53.262321, 'long': -2.141074},
        {'name': 'NHS MULBERRY WARD', 'address': 'Leighton Hospital Middlewich Road, Mulberry Ward Victoria Road, Macclesfield, Cheshire', 'lat': 53.263065, 'long': -2.150297},
        {'name': 'NHS WELLSPRINGS HOSPITAL SITE', 'address': 'Wellsprings Hospital Site Cheddon Road Taunton, Rydon Ward 1', 'lat': 51.032894, 'long': -3.101928},
        {'name': 'NHS MINEHEAD COMMUNITY HOSPITAL', 'address': 'Luttrell Way, Minehead, Somerset', 'lat': 51.200109, 'long': -3.461912},
        {'name': 'NHS MUSGROVE PARK HOSPITAL', 'address': 'Parkfield Dr in Taunton', 'lat': 51.011569, 'long': -3.121702},
        {'name': 'NHS YEOVIL HOSPITAL', 'address': 'Higher Kingston, Yeovil, Somerset', 'lat': 50.944843, 'long': -2.634712},
        {'name': 'NHS ROWAN WARD 1', 'address': 'Rowan ward 1 and 2 Summerlands Hospital Site 56 Preston Road Yeovil', 'lat': 50.946541, 'long': -2.648116},
        {'name': 'NHS BRIDGWATER COMMUNITY HOSPITAL', 'address': 'Bower Lane, Bridgwater, Somerset', 'lat': 51.140557, 'long': -2.974132},
        {'name': 'NHS BURNHAM ON SEA WAR MEMORIAL HOSP.', 'address': '6 Love Lane, Burnham-On-Sea, Somerset', 'lat': 51.238794, 'long': -2.993884},
        {'name': 'NHS RYDAL UNIT, WHISTON HOSPITAL', 'address': 'Warrington Road, Prescot, Merseyside', 'lat': 53.420469, 'long': -2.784954},

]
