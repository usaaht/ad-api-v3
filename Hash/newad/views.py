from rest_framework import viewsets
from rest_framework.response import Response
from .models import Ad, DailyVisitor
from .serializers import AdSerializer
from rest_framework.views import APIView
from .serializers import DailyVisitorReportSerializer
from rest_framework import status


class AdViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling the creation and updating of Ad objects.
    It also updates the DailyVisitor count for each location associated with the Ad.

    Example Usage:
    ad_viewset = AdViewSet()
    ad_viewset.create(request, *args, **kwargs)
    ad_viewset.update(request, *args, **kwargs)

    Inputs:
    - request: The HTTP request object containing the data for creating or updating an Ad object.
    - args: Additional positional arguments.
    - kwargs: Additional keyword arguments.

    Outputs:
    - serializer.data: The serialized data of the created or updated Ad object.
    - Response: The HTTP response containing the serialized data.
    """

    queryset = Ad.objects.all()
    serializer_class = AdSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new Ad object.

        Inputs:
        - request: The HTTP request object containing the data for creating an Ad object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Outputs:
        - Response: The HTTP response containing the serialized data of the created Ad object.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)
    
    def block_ad_on_location(self, ad_id, location_id):
        """
        Block the Ad on a specific location.

        Inputs:
        - ad_id: The ID of the Ad object.
        - location_id: The ID of the location.

        Outputs:
        - None
        """
        ad = Ad.objects.get(id=ad_id)
        location = ad.locations.filter(id=location_id).first()

        '''Perform the logic to block the Ad on the specific location'''
        if location:
            location.blocked = True
            location.save()
            
    def perform_create(self, serializer):
        """
        Perform the creation of the Ad object and create
        DailyVisitor objects for each location associated with the Ad.

        Inputs:
        - serializer: The serializer object for the Ad object.

        Outputs:
        - None
        """
        ad = serializer.save()
        locations = ad.locations.all()
        for location in locations:
            DailyVisitor.objects.create(ad=ad, location=location)

    def update_daily_visitors(self, ad_id, loc_id, count):
        """
        Update the DailyVisitor count for a specific Ad and location.
        If the updated count exceeds the maximum allowed visitors for the location,
        block the Ad on that specific location.

        Inputs:
        - ad_id: The ID of the Ad object.
        - location_id: The ID of the location.
        - count: The count to be added to the DailyVisitor count.

        Outputs:
        - None
        """
        daily_visitor = DailyVisitor.objects.filter(ad_id=ad_id, location_id=loc_id).first()

        if daily_visitor:
            daily_visitor.count += count
            daily_visitor.save()

            # Check if the updated count exceeds the maximum allowed visitors for the location
            max_visitors = daily_visitor.location.max_visitors

            if daily_visitor.count > max_visitors:
                # Block the Ad on that specific location
                self.block_ad_on_location(ad_id, loc_id)

    def update(self, request, *args, **kwargs):
        """
        Update an existing Ad object.

        Inputs:
        - request: The HTTP request object containing the data for updating an Ad object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Outputs:
        - Response: The HTTP response containing the serialized data of the updated Ad object.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """
        Perform the update of the Ad object and update the DailyVisitor
        count for each location associated with the Ad.

        Inputs:
        - serializer: The serializer object for the Ad object.

        Outputs:
        - None
        """
        instance = serializer.save()
        locations = instance.locations.all()
        for location in locations:
            self.update_daily_visitors(instance.id, location.id, 0)


class DailyVisitorReportView(APIView):
    """
    A view for retrieving the DailyVisitor report for a specific Ad.

    Inputs:
    - request: The HTTP request object.
    - ad_id: The ID of the Ad object.

    Outputs:
    - Response: The HTTP response containing the serialized data of the DailyVisitor report.
    """
    def get(self, request, ad_id):
        try:
            daily_visitors = DailyVisitor.objects.filter(ad_id=ad_id)
            serializer = DailyVisitorReportSerializer(daily_visitors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DailyVisitor.DoesNotExist:
            return Response({'detail': 'Ad not found'}, status=status.HTTP_404_NOT_FOUND)


class BlockAdView(APIView):
    def post(self, request, ad_id, location_id):
        ad_viewset = AdViewSet()
        ad_viewset.block_ad_on_location(ad_id, location_id)
        return Response({'detail': 'Ad blocked successfully'}, status=status.HTTP_200_OK)
    
